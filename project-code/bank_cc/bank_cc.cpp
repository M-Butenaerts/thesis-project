#include "shim.h"
#include "logging.h"
#include <string>
#include <vector>
#include <cstring>
#include <cstdint>
#include <stdexcept>
#include <limits>
#include <numeric>
#include <parson.h>

#define OK "OK"
#define MAX_BUF 1024

static inline bool parseI64(const std::string& s, int64_t& v) {
    try {
        size_t pos = 0;
        long long t = std::stoll(s, &pos, 10);
        if (pos != s.size()) return false;
        v = static_cast<int64_t>(t);
        return true;
    } catch (...) { return false; }
}

static inline bool willAddOverflow(int64_t a, int64_t b) {
    if (b > 0 && a > std::numeric_limits<int64_t>::max() - b) return true;
    if (b < 0 && a < std::numeric_limits<int64_t>::min() - b) return true;
    return false;
}
static inline void put_state_bytes (
    const char* key,
    const void* data,
    uint32_t len,
    shim_ctx_ptr_t ctx
) {
    std::vector<uint8_t> tmp(len);
    if (len) std::memcpy(tmp.data(), data, len);
    put_state(key, tmp.data(), len, ctx);
}


static bool load_account(
    const std::string& acc_name,
    std::string& json_buf,
    JSON_Value*& root_out,
    JSON_Object*& obj_out,
    shim_ctx_ptr_t ctx
) {
    uint32_t len = 0;
    uint8_t  buf[MAX_BUF];
    get_state(acc_name.c_str(), buf, sizeof(buf), &len, ctx);
    if (len == 0) return false;

    json_buf.assign(reinterpret_cast<const char*>(buf), len);
    json_buf.push_back('\0');
    
    JSON_Value* root = json_parse_string(json_buf.c_str());
    if (!root || json_value_get_type(root) != JSONObject) {
        if (root) json_value_free(root);
        return false;
    }
    root_out = root;
    obj_out  = json_value_get_object(root);
    return true;
}

static bool save_account(
    const std::string& acc_name,
    JSON_Value* root,
    shim_ctx_ptr_t ctx)
{
    char* serialized = json_serialize_to_string(root);
    if (!serialized) return false;
    size_t out_len = std::strlen(serialized);
    if (out_len > MAX_BUF) {
        json_free_serialized_string(serialized);
        return false;
    }
    
    put_state_bytes(acc_name.c_str(), serialized, static_cast<uint32_t>(out_len), ctx);
    json_free_serialized_string(serialized);
    
    return true;
}

static bool get_amount_i64(JSON_Object* obj, int64_t& out) {
    const char* amount = json_object_get_string(obj, "amount");
    if (!amount) return false;
    return parseI64(amount, out);
}

static void set_amount_i64(JSON_Object* obj, int64_t v) {
    std::string s = std::to_string(v);
    json_object_set_string(obj, "amount", s.c_str());
}

static bool get_seq_i64(JSON_Object* obj, int64_t& out) {
    const char* seq = json_object_get_string(obj, "seq");
    if (!seq) return false;
    return parseI64(std::string(seq), out);
}

static void set_seq_i64(JSON_Object* obj, int64_t v) {
    std::string s = std::to_string(v);
    json_object_set_string(obj, "seq", s.c_str());
}

static bool get_date(JSON_Object* obj, int64_t& out) {
    const char* date = json_object_get_string(obj, "date");
    if (!date) return false;
    return parseI64(date, out);
}

static void set_date(JSON_Object* obj, int64_t v) {
    std::string s = std::to_string(v);
    json_object_set_string(obj, "date", s.c_str());
}

static bool increment_seq(JSON_Object* obj) {
    int64_t seq;
    if (!get_seq_i64(obj, seq)) return false;
    if (willAddOverflow(seq, 1)) return false;
    set_seq_i64(obj, seq + 1);
    return true;
}

int invoke(uint8_t* response,
    uint32_t max_response_len,
    uint32_t* actual_response_len,
    shim_ctx_ptr_t ctx)
{
    std::string function_call;
    std::vector<std::string> params;
    get_func_and_params(function_call, params, ctx);

    std::string joined = (params.empty())
        ? "(none)"
        : std::accumulate(std::next(params.begin()), params.end(), params[0], [](const std::string& a, const std::string& b){ return a + ", " + b; });
    
    LOG_DEBUG("BankCC: Function: %s, Params: %s", function_call.c_str(), joined.c_str());

    std::string result;

    if (function_call == "createAccount") {
        
        if (params.size() != 3) { LOG_DEBUG("BankCC: bad arguments."); return -1; }
        const std::string& acc_name = params[0];

        uint32_t acc_bytes_len = 0;
        uint8_t  acc_bytes[MAX_BUF];
        get_state(acc_name.c_str(), acc_bytes, sizeof(acc_bytes), &acc_bytes_len, ctx);
        
        if (acc_bytes_len > 0) { LOG_DEBUG("BankCC: account already exists."); return -1; }

        const std::string& ss = params[1];
        const std::string& date = params[2];

        JSON_Value*  root = json_value_init_object();
        JSON_Object* obj  = json_value_get_object(root);
        
        json_object_set_string(obj, "ss",   ss.c_str());
        json_object_set_string(obj, "sk",   "");
        json_object_set_string(obj, "date", date.c_str());
        json_object_set_string(obj, "amount", "0"); 
        json_object_set_string(obj, "seq", "1"); 
        
        if (!save_account(acc_name, root, ctx)) {
            json_value_free(root);
            LOG_DEBUG("BankCC: save failed");
            return -1;
        }
        json_value_free(root);
        result = OK;
    }

    else if (function_call == "getAccount") {
        if (params.size() != 1) { LOG_DEBUG("BankCC: bad args."); return -1; }
        const std::string& acc_name = params[0];

        std::string json_copy;
        JSON_Value* root = nullptr;
        JSON_Object* obj = nullptr;
        if (!load_account(acc_name, json_copy, root, obj, ctx)) {
            LOG_DEBUG("BankCC: account not found or bad JSON.");
            return -1;
        }

        if (!json_object_has_value_of_type(obj, "seq", JSONString)) {
            json_object_set_string(obj, "seq", "0");
            if (!save_account(acc_name, root, ctx)) {
                json_value_free(root);
                LOG_DEBUG("BankCC: save failed (seq init).");
                return -1;
            }
        }

        char* ser = json_serialize_to_string(root);
        if (!ser) { json_value_free(root); return -1; }
        result.assign(ser);
        json_free_serialized_string(ser);

        json_value_free(root);
    }

    else if (function_call == "deposit") {
        if (params.size() != 2) { LOG_DEBUG("BankCC: bad args."); return -1; }
        const std::string& acc_name = params[0];
        int64_t delta;
        if (!parseI64(params[1], delta) || delta <= 0) {
            LOG_DEBUG("BankCC: amount must be positive integer.");
            return -1;
        }

        std::string json_buf;
        JSON_Value* root = nullptr;
        JSON_Object* obj = nullptr;
        if (!load_account(acc_name, json_buf, root, obj, ctx)) {
            LOG_DEBUG("BankCC: account not found.");
            return -1;
        }

        int64_t bal;
        if (!get_amount_i64(obj, bal)) { json_value_free(root); return -1; }
        if (willAddOverflow(bal, delta)) {
            json_value_free(root);
            LOG_DEBUG("BankCC: overflow.");
            return -1;
        }
        bal += delta;
        set_amount_i64(obj, bal);
        if (!increment_seq(obj)) { json_value_free(root); LOG_DEBUG("BankCC: seq missing/overflow."); return -1; }

        if (!save_account(acc_name, root, ctx)) {
            json_value_free(root);
            LOG_DEBUG("BankCC: save failed.");
            return -1;
        }
        json_value_free(root);
        result = OK;
    }

    else if (function_call == "withdrawal") {
        if (params.size() != 2) { LOG_DEBUG("BankCC: bad args."); return -1; }
        const std::string& acc_name = params[0];
        int64_t delta;
        if (!parseI64(params[1], delta) || delta <= 0) {
            LOG_DEBUG("BankCC: amount must be positive integer.");
            return -1;
        }

        std::string json_buf;
        JSON_Value* root = nullptr;
        JSON_Object* obj = nullptr;
        if (!load_account(acc_name, json_buf, root, obj, ctx)) {
            LOG_DEBUG("BankCC: account not found.");
            return -1;
        }

        int64_t bal;
        if (!get_amount_i64(obj, bal)) { json_value_free(root); return -1; }
        
        // can be negative
        bal -= delta;
        
        set_amount_i64(obj, bal);
        if (!increment_seq(obj)) { json_value_free(root); LOG_DEBUG("BankCC: seq missing/overflow."); return -1; }

        if (!save_account(acc_name, root, ctx)) {
            json_value_free(root);
            LOG_DEBUG("BankCC: save failed");
            return -1;
        }
        json_value_free(root);
        result = OK;
    }

    else if (function_call == "transfer") {
        if (params.size() != 3) { LOG_DEBUG("BankCC: bad args."); return -1; }
        const std::string& from = params[0];
        const std::string& to   = params[1];
        if (from == to) { LOG_DEBUG("BankCC: same accounts."); return -1; }

        int64_t amount;
        if (!parseI64(params[2], amount) || amount <= 0) {
            LOG_DEBUG("BankCC: amount must be positive integer.");
            return -1;
        }

        std::string json_from, json_to;
        JSON_Value* root_from = nullptr; JSON_Object* obj_from = nullptr;
        JSON_Value* root_to   = nullptr; JSON_Object* obj_to   = nullptr;

        if (!load_account(from, json_from, root_from, obj_from, ctx)) {
            LOG_DEBUG("BankCC: from account not found."); return -1;
        }
        if (!load_account(to,   json_to,   root_to,   obj_to,   ctx)) {
            json_value_free(root_from);
            LOG_DEBUG("BankCC: receiver account not found."); return -1;
        }

        int64_t bal_from, bal_to;
        if (!get_amount_i64(obj_from, bal_from) || !get_amount_i64(obj_to, bal_to)) {
            json_value_free(root_from); json_value_free(root_to); return -1;
        }
        if (bal_from < amount) {
            json_value_free(root_from); json_value_free(root_to);
            LOG_DEBUG("BankCC: insufficient funds.");
            return -1;
        }
        if (willAddOverflow(bal_to, amount)) {
            json_value_free(root_from); json_value_free(root_to);
            LOG_DEBUG("BankCC: overflow.");
            return -1;
        }

        set_amount_i64(obj_from, bal_from - amount);
        set_amount_i64(obj_to,   bal_to   + amount);

        if (!increment_seq(obj_from)) { json_value_free(root_from); LOG_DEBUG("BankCC: seq missing/overflow."); return -1; }

        if (!save_account(from, root_from, ctx) || !save_account(to, root_to, ctx)) {
            json_value_free(root_from); json_value_free(root_to);
            LOG_DEBUG("BankCC: save failed.");
            return -1;
        }

        json_value_free(root_from);
        json_value_free(root_to);
        result = OK;
    }
    else if (function_call == "updateSs") {
        if (params.size() != 2) { LOG_DEBUG("BankCC: bad args."); return -1; }
        const std::string& acc_name = params[0];
        const std::string& new_ss   = params[1];

        std::string json_buf;
        JSON_Value* root = nullptr;
        JSON_Object* obj = nullptr;
        if (!load_account(acc_name, json_buf, root, obj, ctx)) {
            LOG_DEBUG("BankCC: account not found or bad JSON.");
            return -1;
        }
        json_object_set_string(obj, "ss", new_ss.c_str());

        if (!save_account(acc_name, root, ctx)) {
            json_value_free(root);
            LOG_DEBUG("BankCC: save failed");
            return -1;
        }
        json_value_free(root);
        result = OK;
    }
    else if (function_call == "updateSk") {
        if (params.size() != 2) { LOG_DEBUG("BankCC: bad args."); return -1; }
        const std::string& acc_name = params[0];
        const std::string& new_sk   = params[1];

        std::string json_buf;
        JSON_Value* root = nullptr;
        JSON_Object* obj = nullptr;
        if (!load_account(acc_name, json_buf, root, obj, ctx)) {
            LOG_DEBUG("BankCC: account not found or bad JSON.");
            return -1;
        }
        json_object_set_string(obj, "sk", new_sk.c_str());

        if (!save_account(acc_name, root, ctx)) {
            json_value_free(root);
            LOG_DEBUG("BankCC: save failed");
            return -1;
        }
        json_value_free(root);
        result = OK;
    }

    else if (function_call == "updateDate") {
        if (params.size() != 2) { LOG_DEBUG("BankCC: bad args"); return -1; }
        const std::string& acc_name = params[0];
        const std::string& new_date = params[1];

        std::string json_buf;
        JSON_Value* root = nullptr;
        JSON_Object* obj = nullptr;
        if (!load_account(acc_name, json_buf, root, obj, ctx)) {
            LOG_DEBUG("BankCC: account not found or bad JSON");
            return -1;
        }

        json_object_set_string(obj, "date", new_date.c_str());

        if (!save_account(acc_name, root, ctx)) {
            json_value_free(root);
            LOG_DEBUG("BankCC: save failed");
            return -1;
        }
        json_value_free(root);
        result = OK;
    }
    else if (function_call == "setSeq") {
        if (params.size() != 2) { LOG_DEBUG("BankCC: bad args"); return -1; }
        const std::string& acc_name = params[0];
        const std::string& new_seq = params[1];

        std::string json_buf;
        JSON_Value* root = nullptr;
        JSON_Object* obj = nullptr;
        if (!load_account(acc_name, json_buf, root, obj, ctx)) {
            LOG_DEBUG("BankCC: account not found or bad JSON");
            return -1;
        }

        json_object_set_string(obj, "seq", new_seq.c_str());

        if (!save_account(acc_name, root, ctx)) {
            json_value_free(root);
            LOG_DEBUG("BankCC: save failed");
            return -1;
        }
        json_value_free(root);
        result = OK;
    }

    else {
        LOG_DEBUG("BankCC: unknown function '%s'", function_call.c_str());
        return -1;
    }

    const uint32_t need = static_cast<uint32_t>(result.size());
    if (need > max_response_len) {
        *actual_response_len = 0;
        LOG_DEBUG("BankCC: response buffer too small (need %u, have %u)", need, max_response_len);
        return -1;
    }
    std::memcpy(response, result.data(), need);
    *actual_response_len = need;
    return 0;
}





// // ---------- helpers ----------
// static inline std::string kAcct(const std::string& name) {
//     return "acct:" + name;
// }

// static inline void putI64(const std::string& key, int64_t v, shim_ctx_ptr_t ctx) {
//     uint8_t buf[sizeof(int64_t)];
//     std::memcpy(buf, &v, sizeof(int64_t));
//     put_state(key.c_str(), buf, sizeof(int64_t), ctx);
// }

// static inline bool getI64(const std::string& key, int64_t& out, shim_ctx_ptr_t ctx) {
//     uint8_t buf[MAX_BUF];
//     uint32_t len = 0;
//     get_state(key.c_str(), buf, sizeof(buf), &len, ctx);
//     if (len == 0) return false;
//     if (len != sizeof(int64_t)) {
//         LOG_DEBUG("bankCC: unexpected length %u for key %s", len, key.c_str());
//         return false;
//     }
//     std::memcpy(&out, buf, sizeof(int64_t));
//     return true;
// }

// static inline bool willAddOverflow(int64_t a, int64_t b) {
//     if (b > 0 && a > std::numeric_limits<int64_t>::max() - b) return true;
//     if (b < 0 && a < std::numeric_limits<int64_t>::min() - b) return true;
//     return false;
// }

// static inline bool parseI64(const std::string& s, int64_t& v) {
//     try {
//         size_t pos = 0;
//         long long t = std::stoll(s, &pos, 10);
//         if (pos != s.size()) return false;
//         v = static_cast<int64_t>(t);
//         return true;
//     } catch (...) { return false; }
// }

// // ---------- operations ----------
// static std::string createAccount(const std::string& name, int64_t initial, shim_ctx_ptr_t ctx) {
//     LOG_DEBUG("bankCC: createAccount(%s, %lld)", name.c_str(), (long long)initial);
//     int64_t tmp;
//     if (getI64(kAcct(name), tmp, ctx)) return ALREADY_EXISTS;
//     if (initial < 0) return BAD_ARGS;
//     putI64(kAcct(name), initial, ctx);
//     return OK;
// }

// static std::string deposit(const std::string& name, int64_t amount, shim_ctx_ptr_t ctx) {
//     LOG_DEBUG("bankCC: deposit(%s, %lld)", name.c_str(), (long long)amount);
//     if (amount <= 0) return AMOUNT_MUST_BE_POSITIVE;
//     int64_t bal;
//     if (!getI64(kAcct(name), bal, ctx)) return NOT_FOUND;
//     if (willAddOverflow(bal, amount)) return BAD_ARGS;
//     bal += amount;
//     putI64(kAcct(name), bal, ctx);
//     return OK;
// }

// static std::string withdrawal(const std::string& name, int64_t amount, shim_ctx_ptr_t ctx) {
//     LOG_DEBUG("bankCC: withdrawal(%s, %lld)", name.c_str(), (long long)amount);
//     if (amount <= 0) return AMOUNT_MUST_BE_POSITIVE;
//     int64_t bal;
//     if (!getI64(kAcct(name), bal, ctx)) return NOT_FOUND;
//     if (bal < amount) return INSUFFICIENT_FUNDS;
//     bal -= amount;
//     putI64(kAcct(name), bal, ctx);
//     return OK;
// }

// static std::string transfer(const std::string& from, const std::string& to, int64_t amount, shim_ctx_ptr_t ctx) {
//     LOG_DEBUG("bankCC: transfer(%s -> %s, %lld)", from.c_str(), to.c_str(), (long long)amount);
//     if (from == to) return BAD_ARGS;
//     if (amount <= 0) return AMOUNT_MUST_BE_POSITIVE;

//     int64_t fromBal, toBal;
//     if (!getI64(kAcct(from), fromBal, ctx)) return NOT_FOUND;
//     if (!getI64(kAcct(to), toBal, ctx)) return NOT_FOUND;
//     if (fromBal < amount) return INSUFFICIENT_FUNDS;
//     if (willAddOverflow(toBal, amount)) return BAD_ARGS;

//     fromBal -= amount;
//     toBal   += amount;

//     // Write both updates in the same transaction to leverage Fabric MVCC
//     putI64(kAcct(from), fromBal, ctx);
//     putI64(kAcct(to),   toBal,   ctx);
//     return OK;
// }

// static std::string getAccount(const std::string& name, shim_ctx_ptr_t ctx) {
//     int64_t bal;
//     if (!getI64(kAcct(name), bal, ctx)) return NOT_FOUND;
//     return name + ":" + std::to_string(bal);
// }

// // ---------- invoke ----------
// int invoke(uint8_t* response,
//            uint32_t max_response_len,
//            uint32_t* actual_response_len,
//            shim_ctx_ptr_t ctx)
// {
//     std::string fn;
//     std::vector<std::string> p;
//     get_func_and_params(fn, p, ctx);
//     std::string res;

//     try {
//         if (fn == "createAccount") {
//             if (p.size() < 1 || p.size() > 2) return -1;
//             int64_t initial = 0;
//             if (p.size() == 2 && !parseI64(p[1], initial)) return -1;
//             res = createAccount(p[0], initial, ctx);

//         } else if (fn == "deposit") {
//             if (p.size() != 2) return -1;
//             int64_t amount; if (!parseI64(p[1], amount)) return -1;
//             res = deposit(p[0], amount, ctx);

//         } else if (fn == "withdrawal") {
//             if (p.size() != 2) return -1;
//             int64_t amount; if (!parseI64(p[1], amount)) return -1;
//             res = withdrawal(p[0], amount, ctx);

//         } else if (fn == "transfer") {
//             if (p.size() != 3) return -1;
//             int64_t amount; if (!parseI64(p[2], amount)) return -1;
//             res = transfer(p[0], p[1], amount, ctx);

//         } else if (fn == "getAccount") {
//             if (p.size() != 1) return -1;
//             res = getAccount(p[0], ctx);

//         } else {
//             LOG_DEBUG("bankCC: UNKNOWN function '%s'", fn.c_str());
//             return -1;
//         }
//     } catch (const std::exception& e) {
//         LOG_DEBUG("bankCC: exception: %s", e.what());
//         return -1;
//     }

//     const uint32_t need = static_cast<uint32_t>(res.size());
//     if (need > max_response_len) {
//         *actual_response_len = 0;
//         LOG_DEBUG("bankCC: response buffer too small (need %u, have %u)", need, max_response_len);
//         return -1;
//     }
//     std::memcpy(response, res.data(), need);
//     *actual_response_len = need;
//     return 0;
// }
