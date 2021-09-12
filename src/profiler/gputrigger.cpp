#include "gputrigger.h"

#include <sanitizer.h>
#include <string>
#include <unistd.h>

#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <sys/syscall.h>
#include <vector>
//#define DYN_FN_NAME(f) f ## _fn
#define SANITIZER_FN_NAME(f) f

#define SANITIZER_FN(fn, args)                                                 \
  static SanitizerResult(*SANITIZER_FN_NAME(fn)) args

#define GPUTRIGGER_SANITIZER_CALL(fn, args)                                    \
  {                                                                            \
    SanitizerResult status = SANITIZER_FN_NAME(fn) args;                       \
    if (status != SANITIZER_SUCCESS) {                                         \
      sanitizer_error_report(status, #fn);                                     \
    }                                                                          \
  }

#define GPUTRIGGER_SANITIZER_CALL_NO_CHECK(fn, args)                           \
  { SANITIZER_FN_NAME(fn) args; }

static Sanitizer_SubscriberHandle sanitizer_subscriber_handle;

struct GPUCallTree {
  std::string kernel_name;
  int gridDim_x, gridDim_y, gridDim_z, blockDim_x, blockDim_y, blockDim_z;
}

std::vector<GPUCallTree>
    gpu_calltree_vector;

static void sanitizer_subscribe_callback(void *userdata,
                                         Sanitizer_CallbackDomain domain,
                                         Sanitizer_CallbackId cbid,
                                         const void *cbdata) {

  if (domain == SANITIZER_CB_DOMAIN_LAUNCH) {
    Sanitizer_LaunchData *ld = (Sanitizer_LaunchData *)cbdata;
    static __thread dim3 grid_size = {0, 0, 0};
    static __thread dim3 block_size = {0, 0, 0};
    if (cbid == SANITIZER_CBID_LAUNCH_BEGIN) {
      grid_size.x = ld->gridDim_x;
      grid_size.y = ld->gridDim_y;
      grid_size.z = ld->gridDim_z;
      block_size.x = ld->blockDim_x;
      block_size.y = ld->blockDim_y;
      block_size.z = ld->blockDim_z;
      PRINT("Sanitizer-> Launch kernel %s <%d, %d, %d>:<%d, %d, %d>, \n" ld
                ->functionName,
            ld->gridDim_x, ld->gridDim_y, ld->gridDim_z, ld->blockDim_x,
            ld->blockDim_y, ld->blockDim_z);

      // @findhao: add to buffer
      GPUCallTree tmp = {ld->functionName, ld->gridDim_x,  ld->gridDim_y,
                         ld->gridDim_z,    ld->blockDim_x, ld->blockDim_y,
                         ld->blockDim_z};
      gpu_calltree_vector.push_back(tmp);
    }
  }
}

std::vector<GPUCallTree> get_gpu_calltree() { return gpu_calltree_vector; }

int sanitizer_callbacks_subscribe() {

  pid_t pid = getpid();
  printf("PID: %d\n", pid);
  const char *GPUPUNK_DEBUG_raw = getenv("GPUPUNK_DEBUG");
  int GPUPUNK_DEBUG = 0;
  if (GPUPUNK_DEBUG_raw) {
    char *tmp;
    GPUPUNK_DEBUG = strtol(GPUPUNK_DEBUG_raw, &tmp, 10);
  }
  if (GPUPUNK_DEBUG) {
    while (GPUPUNK_DEBUG)
      ;
  }

  // sanitizer_buffer_config(DEFAULT_GPU_PATCH_RECORD_NUM,
  // DEFAULT_BUFFER_POOL_SIZE);

  GPUTRIGGER_SANITIZER_CALL(
      sanitizerSubscribe,
      (&sanitizer_subscriber_handle, sanitizer_subscribe_callback, NULL));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (1, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_LAUNCH));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (1, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_UVM));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (1, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_RESOURCE));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (1, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_MEMCPY));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (1, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_MEMSET));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (1, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_DRIVER_API));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (1, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_RUNTIME_API));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (1, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_SYNCHRONIZE));

  //    sanitizer_process_init();
  //    sanitizer_device_flush();
  //    sanitizer_device_shutdown();

  return 0;
}

int sanitizer_callbacks_unsubscribe() {
  GPUTRIGGER_SANITIZER_CALL(sanitizerUnsubscribe,
                            (sanitizer_subscriber_handle));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerSubscribe,
      (&sanitizer_subscriber_handle, sanitizer_subscribe_callback, NULL));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (0, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_LAUNCH));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (0, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_UVM));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (0, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_RESOURCE));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (0, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_MEMCPY));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (0, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_MEMSET));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (0, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_DRIVER_API));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (0, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_RUNTIME_API));
  GPUTRIGGER_SANITIZER_CALL(
      sanitizerEnableDomain,
      (0, sanitizer_subscriber_handle, SANITIZER_CB_DOMAIN_SYNCHRONIZE));
}