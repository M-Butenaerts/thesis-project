import glob
import subprocess



loc = "/etc/hyperledger/peer-scripts/"

def log(text, file="/tmp/log.txt"):
    with open(file, "a") as f:
        f.write(f"{text}\n")

def set_up_kyber():
    # KEY GEN
    try:
        kyber_c_files = glob.glob(f"{loc}kyber/kyber/ref/*.c")
        command = ["gcc", "-o", f"{loc}kyber/get_key_gen", f"{loc}kyber/get_key_gen.c"] + kyber_c_files + [f"-I{loc}kyber/kyber/ref", "-std=c99"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        log(("STDOUT:", result.stdout))
        log(("STDERR:", result.stderr))
    # DEBUGS
    except subprocess.CalledProcessError as e:
        log(("Compilation failed."))
        log(("STDOUT:", e.stdout))
        log(("STDERR:", e.stderr))
        return False

    except Exception as e:
        log(("Unexpected error at key gen:", e))
        
        return False

    # ENCAPS
    try:
        kyber_c_files = glob.glob(f"{loc}kyber/kyber/ref/*.c")
        command = ["gcc", "-o", f"{loc}kyber/get_encaps", f"{loc}kyber/get_encaps.c"] + kyber_c_files + [f"-I{loc}kyber/kyber/ref", "-std=c99"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        log(("STDOUT:", result.stdout))
        log(("STDERR:", result.stderr))
    # DEBUGS
    except subprocess.CalledProcessError as e:
        log("Compilation failed.")
        log(("STDOUT:", e.stdout))
        log(("STDERR:", e.stderr))
        return False

    except Exception as e:
        log(("Unexpected error:", e))
        log(e)
        return False
    
    # DECAPS
    try:
        kyber_c_files = glob.glob(f"{loc}kyber/kyber/ref/*.c")
        command = ["gcc", "-o", f"{loc}kyber/get_decaps", f"{loc}kyber/get_decaps.c"] + kyber_c_files + [f"-I{loc}kyber/kyber/ref", "-std=c99"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        log(("STDOUT:", result.stdout))
        log(("STDERR:", result.stderr))
    # DEBUGS
    except subprocess.CalledProcessError as e:
        log("Compilation failed.")
        log(("STDOUT:", e.stdout))
        log(("STDERR:", e.stderr))
        return False

    except Exception as e:
        log(("Unexpected error:", e))
        return False

    return True


def key_gen():
    try: 
        command = [f"{loc}kyber/get_key_gen"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        pk = str(result).split("\\n")[1]
        sk = str(result).split("\\n")[4]
        return pk, sk
    except:
        log("failed to create executable file for key_gen.")
        return False

def encaps(pk):
    try: 
        command = [f"{loc}kyber/get_encaps", pk]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        ct = str(result).split("\\n")[1]
        ss = str(result).split("\\n")[4]
        return ct, ss
    except Exception as e:
        log(e)
        log("failed to execute encaps.")
        return False

def decaps(sk, ct):
    try: 
        command = [f"{loc}kyber/get_decaps", sk, ct]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        ss = str(result).split("\\n")[1]
        return ss
    except:
        log("failed to create executable file for decaps.")
        return False
    