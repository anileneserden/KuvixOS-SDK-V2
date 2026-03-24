#pragma once

class App {
public:
    App(void* state) : state(state) {}

protected:
    void* state;
};