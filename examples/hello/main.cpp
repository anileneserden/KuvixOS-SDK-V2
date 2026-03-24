#include <stdint.h>
#include <kvx_c/kuvixos.h>

extern "C" {
    extern const unsigned char _binary_examples_hello_app_json_start[];
    extern const unsigned char _binary_examples_hello_app_json_end[];
}

static void on_draw(const kvx_api_t* api) {
    if (!api) return;
    api->fill_rect(0, 0, 400, 300, 0x2C3E50);
    api->text(10, 10, 0xFFFFFF, "KuvixOS KEF APP");
}

extern "C" __attribute__((used, section(".text._start")))
int _start(const kvx_api_t* api, kvx_kef_app_t* out_vtbl) {
    (void)api;
    if (!out_vtbl) return -1;

    out_vtbl->on_draw = on_draw;
    out_vtbl->ui_json = (const char*)_binary_examples_hello_app_json_start;
    out_vtbl->ui_json_size =
        (uint32_t)(_binary_examples_hello_app_json_end - _binary_examples_hello_app_json_start);

    return 0;
}