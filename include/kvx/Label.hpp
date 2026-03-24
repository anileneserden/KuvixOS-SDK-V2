#pragma once

#include <kvx/App.hpp>

class Label {
public:
    Label(kef_minimal_state_t* st, const char* id)
        : st(st), id(id) {}

    void setText(const char* text) {
        kef_set_text(st, id, text);
    }

private:
    kef_minimal_state_t* st;
    const char* id;
};