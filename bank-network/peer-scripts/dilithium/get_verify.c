#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "/etc/hyperledger/peer-scripts/dilithium/dilithium/ref/api.h"


#define CRYPTO_PUBLICKEYBYTES pqcrystals_dilithium2_ref_PUBLICKEYBYTES
// #define CRYPTO_SECRETKEYBYTES pqcrystals_dilithium2_ref_SECRETKEYBYTES
#define CRYPTO_BYTES pqcrystals_dilithium2_ref_BYTES

// #define crypto_sign_keypair pqcrystals_dilithium2_ref_keypair
// #define crypto_sign_signature pqcrystals_dilithium2_ref_signature
#define crypto_sign_verify pqcrystals_dilithium2_ref_verify

int hex_to_bytes(const char *hex, uint8_t *out, size_t out_len) {
    size_t len = strlen(hex);
    if (len != out_len * 2) return -1;

    for (size_t i = 0; i < out_len; i++) {
        sscanf(hex + 2*i, "%2hhx", &out[i]);
    }
    return 0;
}

void print_hex(const char *label, const uint8_t *data, size_t len) {
    printf("%s:\n", label);
    for (size_t i = 0; i < len; i++) {
        printf("%02x", data[i]);
    }
    printf("\n\n");
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <message> <signature_hex> <public_key_hex>\n", argv[0]);
        return 1;
    }

    const char *message = argv[1];
    const char *sig_hex = argv[2];
    const char *pk_hex = argv[3];
    size_t siglen = CRYPTO_BYTES;


    size_t mlen = strlen(message);
    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t sig[CRYPTO_BYTES];

    if (hex_to_bytes(sig_hex, sig, CRYPTO_BYTES) != 0) {
        fprintf(stderr, "Invalid signature format or length.\n");
        return 1;
    }

    if (hex_to_bytes(pk_hex, pk, CRYPTO_PUBLICKEYBYTES) != 0) {
        fprintf(stderr, "Invalid public key format or length.\n");
        return 1;
    }

    const uint8_t *ctx = NULL;
    size_t ctxlen = 0;

    int valid = crypto_sign_verify(sig, siglen, (const uint8_t *)message, mlen, ctx, ctxlen, pk);

    if (valid == 0) {
        printf("Signature is VALID\n");
    } else {
        printf("Signature is INVALID\n");
    }

    return 0;
}