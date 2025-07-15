#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "/etc/hyperledger/peer-scripts/kyber/kyber/ref/api.h"
#include "/etc/hyperledger/peer-scripts/kyber/kyber/ref/kem.h"

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
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <ciphertext_hex>\n", argv[0]);
        return 1;
    }

    uint8_t sk[CRYPTO_SECRETKEYBYTES];
    uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t ss[CRYPTO_BYTES];

    // Load secret key from file
    // FILE *fsk = fopen("secret.key", "rb");
    if (hex_to_bytes(argv[1], sk, CRYPTO_SECRETKEYBYTES) != 0) {
        fprintf(stderr, "Invalid public key length or format.\n");
        return 1;
    }

    // Convert ciphertext from hex string
    if (hex_to_bytes(argv[2], ct, CRYPTO_CIPHERTEXTBYTES) != 0) {
        fprintf(stderr, "Invalid ciphertext hex length or format.\n");
        return 1;
    }

    // Decapsulate
    crypto_kem_dec(ss, ct, sk);

    // Print shared secret
    print_hex("Shared Secret", ss, CRYPTO_BYTES);

    printf("Decapsulation complete.\n");
    return 0;
}
