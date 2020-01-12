
# 2019 Course is located on [github](https://github.com/natelangholz/stat418-tools-in-datascience)

## [1: Run Rstudio on Docker](https://github.com/natelangholz/stat418-tools-in-datascience/tree/master/week-1)

https://ropenscilabs.github.io/r-docker-tutorial/02-Launching-Docker.html <br>
https://github.com/rocker-org/rocker/issues/303

ifconfig will help to display your ip address

https://github.com/rocker-org/rocker/wiki/Using-the-RStudio-image

`sudo docker run -d -p 8787:8787 -e PASSWORD=<password> USER=asang --name rstudio rocker/rstudio # replace <password> with a password of your choice`

## 3: Unix Commands
Can use unix commands like `cut -d"," -f1 ch05/data/iris.csv | head` in order to parse through csv and txt files

## 5: Deploy on Docker Locally
Commands like the following can be used once you create a model and use docker.

`curl -H "Content-Type: application/json" -X POST -d '{"alcohol":"19","sulphates":".33","volatile_acidity":".25","total_sulfur_dioxide":"10"}' "http://localhost:5000/predict_quality"`

## 6: Deploy Docker on AWS
You can also deploy a model on AWS by:
1. creating an instance
2. ssh into the instance
3. install all docker requirements on instance
4. copy local docker folder to instance
5. ssh back into instance and run files

**Always remember to terminate your instances once you're done!**
