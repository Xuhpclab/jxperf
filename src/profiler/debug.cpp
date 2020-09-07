#include "debug.h"
#include <string.h>

#define MAX_BUFFER_SIZE 256

void print_error_or_info(const char *format ,...) { 
    char buf[MAX_BUFFER_SIZE];
    memset(buf, 0, MAX_BUFFER_SIZE);
    va_list args; 
    va_start(args, format); 
    vsnprintf(buf, MAX_BUFFER_SIZE, format, args); 
    write(STDERR_FILENO, buf, sizeof(buf));
    va_end(args); 
}
