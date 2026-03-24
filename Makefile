# ==========================
# KuvixOS SDK V2 Makefile
# ==========================

CXX = g++
CXXFLAGS = -m32 -ffreestanding -O2 -Wall -Wextra \
           -fno-exceptions -fno-rtti -nostdlib \
           -Iinclude

BUILD = build
TARGET = $(BUILD)/hello.o

SRC = examples/hello/main.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	@mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -rf $(BUILD)