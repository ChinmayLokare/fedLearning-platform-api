# Dockerfile for Spring Boot app
FROM openjdk:17-jdk-slim
ARG JAR_FILE=target/*.jar
COPY ${JAR_FILE} app.jar
# Add user and group for security (optional but good practice)
# RUN groupadd -r spring && useradd -r -g spring spring
# USER spring
ENTRYPOINT ["java","-jar","/app.jar"]
# Expose port if your app.properties specifies a port other than 8080
EXPOSE 8081