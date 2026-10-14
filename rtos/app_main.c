/*
 * app_main.c - Station météo : tâche RTOS périodique (FreeRTOS, MPS2-AN385)
 * Envoie une ligne "T,H,P" par seconde sur l'UART0 (ex : 22.5,55.0,1013.2)
 */
#include "FreeRTOS.h"
#include "task.h"
#include "app_main.h"

#include <stdio.h>
#include <stdint.h>

/* ---------- UART0 de la carte MPS2-AN385 (CMSDK UART) ---------- */
#define UART0_BASE      0x40004000UL
#define UART0_DATA      ( *( volatile uint32_t * ) ( UART0_BASE + 0x00 ) )
#define UART0_STATE     ( *( volatile uint32_t * ) ( UART0_BASE + 0x04 ) )
#define UART0_CTRL      ( *( volatile uint32_t * ) ( UART0_BASE + 0x08 ) )
#define UART0_BAUDDIV   ( *( volatile uint32_t * ) ( UART0_BASE + 0x10 ) )

static void uart_init( void )
{
    UART0_BAUDDIV = 16;
    UART0_CTRL = 1;                 /* émission activée */
}

static void uart_putc( char c )
{
    while( UART0_STATE & 1 ) { }    /* attend que le tampon d'émission soit libre */
    UART0_DATA = ( uint32_t ) c;
}

static void uart_put_uint( unsigned int v )
{
    char buf[ 10 ];
    int n = 0;

    do { buf[ n++ ] = ( char ) ( '0' + ( v % 10 ) ); v /= 10; } while( v > 0 );
    while( n > 0 ) { uart_putc( buf[ --n ] ); }
}

/* Affiche une valeur en dixièmes : 225 -> "22.5" */
static void uart_put_tenths( unsigned int v )
{
    uart_put_uint( v / 10 );
    uart_putc( '.' );
    uart_putc( ( char ) ( '0' + ( v % 10 ) ) );
}

/* ---------- Mesures simulées : signal en triangle ---------- */
static int tri( uint32_t n, int periode, int amp )
{
    int x = ( int ) ( n % periode );
    int demi = periode / 2;
    int d = ( x < demi ) ? x : periode - x;

    return ( d * amp ) / demi;
}

/* ---------- Tâche périodique (privilégiée) ---------- */
#define CAPTEUR_STACK_WORDS    512

static StaticTask_t xCapteurTCB;
static StackType_t uxCapteurStack[ CAPTEUR_STACK_WORDS ]
    __attribute__( ( aligned( CAPTEUR_STACK_WORDS * sizeof( StackType_t ) ) ) );

static void prvCapteurTask( void * pvParameters )
{
    TickType_t xLastWake;
    uint32_t n = 0;

    ( void ) pvParameters;

    uart_init();
    xLastWake = xTaskGetTickCount();

    for( ; ; )
    {
        /* Période exacte de 1000 ms : c'est le rôle du temps réel */
        vTaskDelayUntil( &xLastWake, pdMS_TO_TICKS( 1000 ) );

        unsigned int t = 200 + tri( n, 60, 80 );      /* 20.0 à 28.0 C   */
        unsigned int h = 500 + tri( n, 90, 150 );     /* 50.0 à 65.0 %   */
        unsigned int p = 10120 + tri( n, 200, 40 );   /* 1012.0 à 1016.0 */

        uart_put_tenths( t );  uart_putc( ',' );
        uart_put_tenths( h );  uart_putc( ',' );
        uart_put_tenths( p );  uart_putc( '\n' );
        n++;
    }
}

void app_main( void )
{
    /* portPRIVILEGE_BIT : tâche privilégiée (accès direct à l'UART, sans MPU) */
    xTaskCreateStatic( prvCapteurTask,
                       "capteur",
                       CAPTEUR_STACK_WORDS,
                       NULL,
                       ( tskIDLE_PRIORITY + 2 ) | portPRIVILEGE_BIT,
                       uxCapteurStack,
                       &xCapteurTCB );

    vTaskStartScheduler();

    printf( "Returned from vTaskStartScheduler something bad had happened\n" );

    for( ; ; )
    {
    }
}
/*-----------------------------------------------------------*/

void vApplicationStackOverflowHook( TaskHandle_t pxTask,
                                    char * pcTaskName )
{
    ( void ) pxTask;
    ( void ) pcTaskName;

    printf( "Stack Overflow Hook called\n" );

    for( ; ; )
    {
    }
}
/*-----------------------------------------------------------*/

void vApplicationMallocFailedHook( void )
{
    printf( "Application Malloc Failed Hook called\n" );

    for( ; ; )
    {
    }
}
/*-----------------------------------------------------------*/

void vApplicationGetIdleTaskMemory( StaticTask_t ** ppxIdleTaskTCBBuffer,
                                    StackType_t ** ppxIdleTaskStackBuffer,
                                    uint32_t * pulIdleTaskStackSize )
{
    static StaticTask_t xIdleTaskTCB;
    static StackType_t uxIdleTaskStack[ configMINIMAL_STACK_SIZE ];

    *ppxIdleTaskTCBBuffer = &xIdleTaskTCB;
    *ppxIdleTaskStackBuffer = uxIdleTaskStack;
    *pulIdleTaskStackSize = configMINIMAL_STACK_SIZE;
}
/*-----------------------------------------------------------*/

void vApplicationGetTimerTaskMemory( StaticTask_t ** ppxTimerTaskTCBBuffer,
                                     StackType_t ** ppxTimerTaskStackBuffer,
                                     uint32_t * pulTimerTaskStackSize )
{
    static StaticTask_t xTimerTaskTCB;
    static StackType_t uxTimerTaskStack[ configTIMER_TASK_STACK_DEPTH ];

    *ppxTimerTaskTCBBuffer = &xTimerTaskTCB;
    *ppxTimerTaskStackBuffer = uxTimerTaskStack;
    *pulTimerTaskStackSize = configTIMER_TASK_STACK_DEPTH;
}
/*-----------------------------------------------------------*/
