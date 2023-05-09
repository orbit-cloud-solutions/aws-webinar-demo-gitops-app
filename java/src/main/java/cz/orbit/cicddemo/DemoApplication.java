package cz.orbit.cicddemo;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.info.BuildProperties;
import org.springframework.http.HttpHeaders;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class DemoApplication {

    Logger logger = LoggerFactory.getLogger(DemoApplication.class);

    @Autowired
    private BuildProperties buildProperties;


    @RequestMapping("/")
    public ResponseEntity<String> hello(@RequestHeader HttpHeaders headers){

        logger.info("Request logging: " + headers.toString() );

        String backgroundColor = System.getenv("BACKGROUND_COLOR");
        if (backgroundColor == null) {
            backgroundColor = "#f0f0f0"; // Default to light gray if the environment variable is not set
        }

        String responseBody = "<html><body style=\"background-color:" + backgroundColor + ";\"><div style=\"text-align:center;font-size:36px;font-weight:bold;\">CICD Demo</div><div style=\"text-align:center;font-size:24px;\">Version: "+buildProperties.getVersion()+"</div></body></html>";
        
        HttpHeaders responseHeaders = new HttpHeaders();
        responseHeaders.setContentType(MediaType.TEXT_HTML);
        
        return new ResponseEntity<>(responseBody, responseHeaders, HttpStatus.OK);
    }

    public static void main(final String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }

}
