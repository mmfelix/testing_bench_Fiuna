#include <stdlib.h>     //exit()
#include <signal.h>     //signal()
#include <time.h>
#include "ADS1256.h"
#include "stdio.h"
#include <string.h>
#include <sys/time.h>
#include <sys/timeb.h>

void  Handler(int signo)
{
    //System Exit
    printf("\r\nEND                  \r\n");
    DEV_ModuleExit();
    exit(0);
}

int main(int argc, char *argv[])
{
    u_int8_t min, sec;
    double time_recording;
    min = atoi(argv[3]);
    sec = atoi(argv[4]);
    printf("%d:%d\n", min, sec);
    UDOUBLE ADC1, ADC2;
    printf("demo\r\n");
    DEV_ModuleInit();
    
    // Exception handling:ctrl + c
    signal(SIGINT, Handler);

    while(ADS1256_init() == 1){
        printf("\r\nEND                  \r\n");
        DEV_ModuleExit();
        DEV_ModuleInit();
    }
    printf("\nCreating %s.csv file\n", argv[2]);

    struct timeval stop, start;
    struct timespec ts;
    ts.tv_sec = 0;
    ts.tv_nsec = 2;
    
    FILE *fp;
    
    strcat(argv[1], argv[2]);
    strcat(argv[1],".csv");
    fp = fopen(argv[1],"w+");
    fprintf(fp,"time, pressure, flow");
    printf(argv[1]);

    gettimeofday(&start, NULL);
    
    while(1){
        ADC1 = ADS1256_GetChannalValue(0);
        
        nanosleep(&ts, &ts);
        ADC2 = ADS1256_GetChannalValue(1);
        nanosleep(&ts, &ts);
        
        gettimeofday(&stop, NULL);
        time_recording = stop.tv_sec - start.tv_sec + (stop.tv_usec - start.tv_usec)/1000000.0;
        if(time_recording <= (UDOUBLE)(min*60 + sec)){
            fprintf(fp, "\n%lf, %f, %f", time_recording, ADC1*5.0/0x7fffff, ADC2*5.0/0x7fffff);
        }
        else break; 
    }
    
    gettimeofday(&stop, NULL);
    printf("Time in microseconds: %ld us\n", 
    (stop.tv_sec - start.tv_sec)*1000000L
    + stop.tv_usec - start.tv_usec);
    fclose(fp);
    return 0;
}
