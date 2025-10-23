// get_keygen.c
#include <stdio.h>
#include <stdint.h>
#include "api.h"  // Contains Kyber API definitions
#include "kem.h"

int main() {
    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t sk[CRYPTO_SECRETKEYBYTES];

    if (crypto_kem_keypair(pk, sk) != 0) {
        fprintf(stderr, "Key generation failed.\n");
        return 1;
    }

    printf("Public Key (hex):\n");
    for (int i = 0; i < CRYPTO_PUBLICKEYBYTES; i++) {
        printf("%02x", pk[i]);
    }
    printf("\n\n");

    printf("Secret Key (hex):\n");
    for (int i = 0; i < CRYPTO_SECRETKEYBYTES; i++) {
        printf("%02x", sk[i]);
    }
    printf("\n");

    return 0;
}
