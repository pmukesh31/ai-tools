**curl request for inferenece:**

curl -X POST -H "Content-Type: application/json" -d '{
"text": "ପାମ ମିଶନରୀ ଉପରେ କେତେ % ରିହାତି ଧୈର୍ଯ ହୋଇଛି",
"lang" : "ory"
}' http://localhost:8000/

curl -X POST -H "Content-Type: application/json" -d '{
"text": "ପାମ ମିଶନରୀ ଉପରେ କେତେ % ରିହାତି ଧୈର୍ଯ ହୋଇଛି"
}' http://172.17.0.2:8000/

curl -X POST -H "Content-Type: application/json" -d '{
"text": "how to apply for go-sugem scheme for my paddi crop",
"lang" : "eng"
}' http://localhost:8000/



**curl request for update:**

curl -X PUT -H "Content-Type: application/json" -d '{
"text": "ମିଶନରୀ",
"lang" : "ory"
}' http://localhost:8000/

curl -X PUT -H "Content-Type: application/json" -d '{
"text": ["ପାମ ମିଶନରୀ ଉପରେ", "ରିହାତି ଧୈର୍ଯ ହୋଇଛି"]
}' http://localhost:8000/

curl -X PUT -H "Content-Type: application/json" -d '{
"text": "go-sugem",
"lang" : "eng"
}' http://localhost:8000/

curl -X PUT -H "Content-Type: application/json" -d '{
"text": ["how to apply for", "scheme for my paddi crop"],
"lang" : "eng"
}' http://localhost:8000/
