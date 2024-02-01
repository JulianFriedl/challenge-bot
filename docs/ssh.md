**Prerequisites:**
1. Make sure you have the SSH key pair (public and private keys) that you want to use for authentication. If you don't have them, you can generate a new SSH key pair.

**Steps:**

**Generating an SSH Key Pair:**

1. Open your terminal or command prompt on your local machine.

2. Use the following command to generate an SSH key pair. Replace `your_email@example.com` with your email address:

   ```
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```

   This command will generate a new SSH key pair with RSA encryption and a bit length of 4096. You can accept the default file location or specify a custom one.

3. You may be prompted to enter a passphrase. It's optional but recommended for added security. Enter a passphrase and confirm it.

4. Once the key pair is generated, you'll see output similar to this:

   ```
   Your public key has been saved in /home/yourusername/.ssh/id_rsa.pub.
   Your private key has been saved in /home/yourusername/.ssh/id_rsa.
   ```

   Your SSH key pair is now generated, and you have a private key (`id_rsa`) and a public key (`id_rsa.pub`).

   Add the public key do the server you want to connect to.

**Setting the Private Key for SSH Authentication:**

1. Use the `ssh-add` command to add your private key to the SSH agent. Replace `/path/to/your/private/key` with the actual path to your private key file:

   ```
   ssh-add /path/to/your/private/key
   ```

   For example:

   ```
   ssh-add ~/.ssh/id_rsa
   ```

   You will be prompted to enter the passphrase if you set one during key generation.

**Connecting to the VM via SSH:**

1. Open your terminal or command prompt on your local machine.

2. Use the `ssh` command followed by the username and the IP address or hostname of the remote VM. Replace `username` with your actual username and `IP_ADDRESS` with the IP address or hostname of your VM:

   ```
   ssh username@IP_ADDRESS
   ```

3. If this is your first time connecting to the VM from your local machine, you may see a message asking if you want to continue connecting. Type `yes` to confirm.

4. You should now be connected to the remote VM using the SSH key pair you generated.

5. To disconnect and log out from the remote VM, simply type the following command and press Enter:

   ```
   exit
   ```

   This will log you out of the remote VM and return you to your local command prompt.
