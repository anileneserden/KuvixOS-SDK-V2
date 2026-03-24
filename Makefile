# ==========================
# KuvixOS SDK V2 Makefile
# ==========================

CXX = g++
OBJCOPY = objcopy

BUILD = build
APP_NAME = hello

APP_CPP = examples/hello/main.cpp
APP_JSON = examples/hello/app.json

APP_OBJ = $(BUILD)/examples/hello/main.o
APP_JSON_OBJ = $(BUILD)/examples/hello/app_json.o
APP_KEF = $(BUILD)/$(APP_NAME).kef

CXXFLAGS = -m32 -ffreestanding -O2 -Wall -Wextra \
           -fno-pie -fno-exceptions -fno-rtti \
           -nostdlib -nostartfiles \
           -Iinclude \
           -std=c++17

LDFLAGS = -m32 -nostdlib -ffreestanding -fno-pie \
          -Wl,-T,tools/linker_app.ld \
          -Wl,--build-id=none \
          -Wl,--gc-sections

all: $(APP_KEF)

$(APP_OBJ): $(APP_CPP)
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(APP_JSON_OBJ): $(APP_JSON)
	@mkdir -p $(dir $@)
	$(OBJCOPY) -I binary -O elf32-i386 -B i386 $< $@

$(APP_KEF): $(APP_OBJ) $(APP_JSON_OBJ) tools/linker_app.ld
	@mkdir -p $(BUILD)
	$(CXX) $(LDFLAGS) -o $@ $(APP_OBJ) $(APP_JSON_OBJ)

clean:
	rm -rf $(BUILD)