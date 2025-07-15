import glob
import subprocess

loc = "utils/"

def set_up_kyber():
    # KEY GEN
    try:
        kyber_c_files = glob.glob(f"{loc}kyber/kyber/ref/*.c")
        command = ["gcc", "-o", f"{loc}kyber/get_key_gen", f"{loc}kyber/get_key_gen.c"] + kyber_c_files + [f"-I{loc}kyber/kyber/ref", "-std=c99"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    # DEBUGS
    except subprocess.CalledProcessError as e:
        print("Compilation failed.")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

    except Exception as e:
        print("Unexpected error at key gen:", e)
        print(e)
        return False

    # ENCAPS
    try:
        kyber_c_files = glob.glob(f"{loc}kyber/kyber/ref/*.c")
        command = ["gcc", "-o", f"{loc}kyber/get_encaps", f"{loc}kyber/get_encaps.c"] + kyber_c_files + [f"-I{loc}kyber/kyber/ref", "-std=c99"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    # DEBUGS
    except subprocess.CalledProcessError as e:
        print("Compilation failed.")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

    except Exception as e:
        print("Unexpected error:", e)
        print(e)
        return False
    
    # DECAPS
    try:
        kyber_c_files = glob.glob(f"{loc}kyber/kyber/ref/*.c")
        command = ["gcc", "-o", f"{loc}kyber/get_decaps", f"{loc}kyber/get_decaps.c"] + kyber_c_files + [f"-I{loc}kyber/kyber/ref", "-std=c99"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    # DEBUGS
    except subprocess.CalledProcessError as e:
        print("Compilation failed.")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

    except Exception as e:
        print("Unexpected error:", e)
        print(e)
        return False

    return True


def key_gen():
    try: 
        command = [f"./{loc}kyber/get_key_gen"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        pk = str(result).split("\\n")[1]
        sk = str(result).split("\\n")[4]
        return pk, sk
    except:
        print("failed to create executable file for key_gen.")
        return False

def encaps(pk):
    try: 
        command = [f"./{loc}kyber/get_encaps", pk]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        pk = str(result).split("\\n")[1]
        sk = str(result).split("\\n")[4]
        return pk, sk
    except:
        print("failed to create executable file for encaps.")
        return False

def decaps(sk, ct):
    try: 
        command = [f"./{loc}kyber/get_decaps", sk, ct]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        pk = str(result).split("\\n")[1]
        sk = str(result).split("\\n")[4]
        return pk, sk
    except:
        print("failed to create executable file for decaps.")
        return False
    