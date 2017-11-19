#!/bin/bash                                                                     

#NOTE - THIS SCRIPT IS JUST FOR REFRENCE AND IS NOT ACTUALLY USED IN THE OPENSHIFT TEMPLATE
                                                                                
set -x                                                                          
                                                                                
# Use the oc client to get the url for the gogs route and service               
GOGSSVC=$(oc get svc gogs -o template --template='{{.spec.clusterIP}}')         
GOGSROUTE=$(oc get route gogs -o template --template='{{.spec.host}}')          
                                                                                
# Use the oc client to get the postgres variables into the current shell        
eval $(oc env dc/postgresql-gogs --list | grep -v \#)                           
                                                                                
# postgres has a readiness probe, so checking if there is at least one          
# endpoint means postgres is alive and ready, so we can then attempt to install gogs                                                                            
# we're willing to wait 60 seconds for it, otherwise something is wrong.        
x=1                                                                             
oc get ep postgresql-gogs -o yaml | grep "\- addresses:"                        
while [ ! $? -eq 0 ]                                                            
do                                                                              
  sleep 10                                                                      
  x=$(( $x + 1 ))                                                               
                                                                                
  if [ $x -gt 100 ]
  then                                                                          
    exit 255                                                                    
  fi                                                                            
                                                                                
  oc get ep postgresql-gogs -o yaml | grep "\- addresses:"                      
done                                                                            
                                                                                
# now we wait for gogs to be ready in the same way                              
x=1                                                                             
oc get ep gogs -o yaml | grep "\- addresses:"                                   
while [ ! $? -eq 0 ]                                                            
do                                                                              
  sleep 10                                                                      
  x=$(( $x + 1 ))                                                               
                                                                                
  if [ $x -gt 100 ]                                                             
  then                                                                          
    exit 255                                                                    
  fi                                                                            
                                                                                
  oc get ep gogs -o yaml | grep "\- addresses:"                                 
done
# we might catch the router before it's been updated, so wait just a touch      
# more                                                                          
sleep 10                                                                        
                                                                                
RETURN=$(curl -o /dev/null -sL --post302 -w "%{http_code}" http://$GOGSSVC:3000/
install \                                                                       
--form db_type=PostgreSQL \                                                     
--form db_host=postgresql-gogs:5432 \                                           
--form db_user=gogs \                                                           
--form db_passwd=$POSTGRESQL_PASSWORD \                                         
--form db_name=gogs \                                                           
--form ssl_mode=disable \                                                       
--form db_path=data/gogs.db \                                                   
--form "app_name=Gogs: Go Git Service" \                                        
--form repo_root_path=/opt/gogs/data/repositories \                             
--form run_user=gogs \                                                          
--form domain=localhost \                                                       
--form ssh_port=22 \                                                            
--form http_port=3000 \                                                         
--form app_url=http://${GOGSROUTE}/ \                                           
--form log_root_path=/opt/gogs/log \                                            
--form admin_name=gogs \                                                        
--form admin_passwd=password \
--form admin_confirm_passwd=password \                                          
--form admin_email=admin@gogs.com)                                              
                                                                                
if [ $RETURN != "200" ] && [ $RETURN != "302" ]                                 
then                                                                            
  echo "ERROR: Failed to initialize Gogs"                                       
  exit 255                                                                      
fi                                                                              
                                                                                
sleep 10                                                                        
                                                                                
# import github repository                                                      
cat <<EOF > /tmp/data.json                                                      
{                                                                               
  "clone_addr": "https://github.com/OpenShiftInAction/chapter6",                
  "uid": 1,                                                                     
  "repo_name": "openshift-cicd-flask-mongo"                                     
}                                                                               
EOF                                                                             
                                                                                
RETURN=$(curl -o /dev/null -sL -w "%{http_code}" -H "Content-Type: application/json" \                                                                          
-u gogs:password -X POST http://$GOGSSVC:3000/api/v1/repos/migrate -d @/tmp/data.json)                                                                          
                                                                                
if [ $RETURN != "201" ]                                                         
then                                                                            
  echo "ERROR: Failed to imported openshift-cicd-flask-mongo GitHub repo"       
  exit 255                                                                      
fi                                                                              
                                                                                
sleep 5                                                                         
                                                                                
# add webhook to Gogs to trigger pipeline on push                               
cat <<EOF > /tmp/data.json                                                      
{                                                                               
  "type": "gogs",                                                               
  "config": {                                                                   
    "url": "https://openshift.default.svc.cluster.local/oapi/v1/namespaces/${DEV_PROJECT}/buildconfigs/todo-app-flask-mongo/webhooks/ohAfsvBk/generic",         
    "content_type": "json"                                                      
  },                                                                            
  "events": [                                                                   
    "push"                                                                      
  ],                                                                            
  "active": true                                                                
}                                                                               
EOF                                                                             
                                                                                
RETURN=$(curl -o /dev/null -sL -w "%{http_code}" -H "Content-Type: application/json" \                                                                          
-u gogs:password -X POST http://$GOGSSVC:3000/api/v1/repos/gogs/openshift-cicd-flask-mongo/hooks -d @/tmp/data.json)                                            
                                                                                
if [ $RETURN != "201" ]                                                         
then                                                                            
  echo "ERROR: Failed to set webhook"                                           
  exit 255                                                                      
fi                                                                              
                                                                                
                                                                                
export newgiturl=http://$(oc get svc gogs -o=jsonpath='{.spec.clusterIP}'):$(oc get svc gogs -o=jsonpath='{.spec.ports[].port}')/gogs/openshift-cicd-flask-mongo
cho newgiturl=$newgiturl                                                      
export patchstr={\"spec\":{\"source\":{\"git\":{\"uri\":\"$newgiturl\"}}}}      
echo $patchstr                                                                  
oc patch bc todo-app-flask-mongo -p $patchstr                
