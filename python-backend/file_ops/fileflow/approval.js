def get_user_approval(filepath, new_name):
    print(f"\nFile: {filepath}")
    print(f"Suggested name: {new_name}")
    resp = input("Approve rename + move? [y/N]: ").lower()
    return resp == "y"
