FROM public.ecr.aws/docker/library/openjdk:slim

EXPOSE 8080
ADD app.jar app.jar
ENTRYPOINT ["java","-Xms512m","-Xmx1024m","-jar","app.jar"]