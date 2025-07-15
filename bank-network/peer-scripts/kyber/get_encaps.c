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
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <public_key_hex>\n", argv[0]);
        return 1;
    }

    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t ss[CRYPTO_BYTES];

    if (hex_to_bytes(argv[1], pk, CRYPTO_PUBLICKEYBYTES) != 0) {
        fprintf(stderr, "Invalid public key length or format.\n");
        return 1;
    }

    crypto_kem_enc(ct, ss, pk);

    // Save outputs
    // FILE *fct = fopen("ciphertext.bin", "wb");
    // fwrite(ct, 1, CRYPTO_CIPHERTEXTBYTES, fct);
    // fclose(fct);

    // FILE *fss = fopen("shared_secret_sender.bin", "wb");
    // fwrite(ss, 1, CRYPTO_BYTES, fss);
    // fclose(fss);
    print_hex("Ciphertext", ct, CRYPTO_CIPHERTEXTBYTES);
    print_hex("Shared Secret", ss, CRYPTO_BYTES);

    printf("Encapsulation complete.\n");
    return 0;
}

