/* Check two independent Lua ABIs in one process, in both loader orders. */
#include "lua.h"
#include <assert.h>
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>

#define STRINGIFY_INNER(x) #x
#define STRINGIFY(x) STRINGIFY_INNER(x)

struct api {
    lua_State *(*newstate)(void);
    int (*openbase)(lua_State *);
    int (*loadstring)(lua_State *, const char *);
    int (*pcall)(lua_State *, int, int, int, lua_KContext, lua_KFunction);
    const char *(*tolstring)(lua_State *, int, size_t *);
    void (*close)(lua_State *);
    lua_Number (*version)(lua_State *);
};

static void *symbol(void *handle, const char *name) {
    void *value = dlsym(handle, name);
    if (!value)
        fprintf(stderr, "Missing symbol %s: %s\n", name, dlerror());
    assert(value);
    return value;
}

static struct api load_api(void *handle, int private_abi) {
    struct api api;
    api.newstate = symbol(handle, private_abi ? STRINGIFY(luaL_newstate) : "luaL_newstate");
    api.openbase = symbol(handle, private_abi ? STRINGIFY(luaopen_base) : "luaopen_base");
    api.loadstring = symbol(handle, private_abi ? STRINGIFY(luaL_loadstring) : "luaL_loadstring");
    api.pcall = symbol(handle, private_abi ? STRINGIFY(lua_pcallk) : "lua_pcallk");
    api.tolstring = symbol(handle, private_abi ? STRINGIFY(lua_tolstring) : "lua_tolstring");
    api.close = symbol(handle, private_abi ? STRINGIFY(lua_close) : "lua_close");
    api.version = symbol(handle, private_abi ? STRINGIFY(lua_version) : "lua_version");
    return api;
}

static void check_state(struct api *api, const char *expected) {
    lua_State *state = api->newstate();
    assert(state);
    assert(api->openbase(state) == 1);
    assert(api->loadstring(state, "return _VERSION") == 0);
    assert(api->pcall(state, 0, 1, 0, 0, NULL) == 0);
    assert(strcmp(api->tolstring(state, -1, NULL), expected) == 0);
    api->close(state);
}

int main(int argc, char **argv) {
    assert(argc == 4);
    void *native, *parallel;
    if (strcmp(argv[3], "native-first") == 0) {
        native = dlopen(argv[1], RTLD_NOW | RTLD_GLOBAL);
        parallel = dlopen(argv[2], RTLD_NOW | RTLD_GLOBAL);
    } else {
        assert(strcmp(argv[3], "parallel-first") == 0);
        parallel = dlopen(argv[2], RTLD_NOW | RTLD_GLOBAL);
        native = dlopen(argv[1], RTLD_NOW | RTLD_GLOBAL);
    }
    if (!native || !parallel)
        fprintf(stderr, "Library load failed: %s\n", dlerror());
    assert(native && parallel);
    struct api system = load_api(native, 0), isolated = load_api(parallel, 1);
    assert(system.newstate != isolated.newstate);
    assert(symbol(RTLD_DEFAULT, "luaL_newstate") == (void *)system.newstate);
    assert(symbol(RTLD_DEFAULT, STRINGIFY(luaL_newstate)) == (void *)isolated.newstate);
    assert(dlsym(parallel, "luaL_newstate") == NULL);
    assert(isolated.version(NULL) == 505);
    lua_Number native_version = system.version(NULL);
    assert(native_version == 504 || native_version == 505);
    check_state(&system, native_version == 504 ? "Lua 5.4" : "Lua 5.5");
    check_state(&isolated, "Lua 5.5");
    dlclose(parallel);
    dlclose(native);
    printf("Independent native and parallel Lua states: %s\n", argv[3]);
    return 0;
}
