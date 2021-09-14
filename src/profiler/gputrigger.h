#include <sanitizer.h>
#include <sanitizer_result.h>
static void sanitizer_subscribe_callback(void *userdata,
                                         Sanitizer_CallbackDomain domain,
                                         Sanitizer_CallbackId cbid,
                                         const void *cbdata);
int sanitizer_callbacks_subscribe();
int sanitizer_callbacks_unsubscribe();

std::vector<GPUCallTree> get_gpu_calltree();