package com.neuroai.backend;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

@SpringBootApplication
@MapperScan("com.neuroai.backend.mapper")
@ConfigurationPropertiesScan
public class NeuroAiApplication {

    public static void main(String[] args) {
        SpringApplication.run(NeuroAiApplication.class, args);
    }
}
