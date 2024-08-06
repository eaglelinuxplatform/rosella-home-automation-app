from fernet import Fernet

def generate_key():
    """
    The function generates a key for encryption using the Fernet module in Python.
    :return: a generated key using the Fernet module.
    """
    return Fernet.generate_key()



def save_key_to_file(key, file_path):
    with open(file_path, 'wb') as key_file:
        key_file.write(key)

def load_key_from_file(file_path):
    with open(file_path, 'rb') as key_file:
        return key_file.read()

def encrypt_file(file_path, key):
    fernet = Fernet(key)
    with open(file_path, 'rb') as file:
        original_data = file.read()

    encrypted_data = fernet.encrypt(original_data)

    with open(file_path + '.encrypted', 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)

def decrypt_file(file_path, key):
    fernet = Fernet(key)
    with open(file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()

    decrypted_data = fernet.decrypt(encrypted_data)

    with open(file_path[:-10], 'wb') as decrypted_file:  # Remove the '.encrypted' extension
        decrypted_file.write(decrypted_data)

# # Example usage
# file_to_encrypt = 'example.txt'
# key = generate_key()

# # Save the key to a file
# key_file_path = 'e:\Anzal\project23\IoT Gateway\Gwy_structurized_code\gateway\security\secret.key'
# save_key_to_file(key, key_file_path)

# # Encrypt the file using the generated key
# encrypt_file(file_to_encrypt, key)

# # Decrypt the file using the same key
# file_to_decrypt = 'example.txt.encrypted'
# decrypt_file(file_to_decrypt, load_key_from_file(key_file_path))
