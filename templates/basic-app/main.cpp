#include <stdint.h>
#include <kvx_c/kuvixos.h>

static void on_draw(const kvx_api_t* api) {
    if (!api) return;
    api->fill_rect(0, 0, 400, 300, 0x2C3E50);
    api->text(10, 10, 0xFFFFFF, "KuvixOS KEF APP");
}

static const char g_probe_json[] =
    "{\n"
    "  \"window\": {\n"
    "    \"title\": \"Hello\",\n"
    "    \"width\": 320,\n"
    "    \"height\": 180,\n"
    "    \"backgroundColor\": \"#121212\"\n"
    "  },\n"
    "  \"widgets\": [\n"
    "    {\n"
    "      \"id\": \"titleLabel\",\n"
    "      \"type\": \"label\",\n"
    "      \"text\": \"HELLO\",\n"
    "      \"x\": 12,\n"
    "      \"y\": 12,\n"
    "      \"color\": \"#ffffff\"\n"
    "    }\n"
    "  ]\n"
    "}\n";

extern "C" __attribute__((used, section(".text._start")))
int _start(const kvx_api_t* api, kvx_kef_app_t* out_vtbl) {
    (void)api;
    if (!out_vtbl) return -1;

    out_vtbl->on_draw = on_draw;
    out_vtbl->ui_json = g_probe_json;
    out_vtbl->ui_json_size = (uint32_t)(sizeof(g_probe_json) - 1);
    return 0;
}