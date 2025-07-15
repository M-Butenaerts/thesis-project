#include <stdio.h>
#include <stdint.h>
#include "dilithium/ref/api.h"


#define CRYPTO_PUBLICKEYBYTES pqcrystals_dilithium2_ref_PUBLICKEYBYTES
#define CRYPTO_SECRETKEYBYTES pqcrystals_dilithium2_ref_SECRETKEYBYTES
// #define CRYPTO_BYTES pqcrystals_dilithium2_ref_BYTES

#define crypto_sign_keypair pqcrystals_dilithium2_ref_keypair
// #define crypto_sign_signature pqcrystals_dilithium2_ref_signature
// #define crypto_sign_verify pqcrystals_dilithium2_ref_verify

int main() {
    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t sk[CRYPTO_SECRETKEYBYTES];

    // crypto_sign_keypair(pk, sk);
    if (crypto_sign_keypair(pk, sk) != 0) {
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
