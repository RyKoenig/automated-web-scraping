# Web Scraping Automation Setup

This repository provides a step-by-step guide on setting up a fresh Linux server for automated web scraping tasks. It covers the installation and configuration of PostgreSQL, Cronicle (job scheduling), Chrome, and ChromeDriver. This setup is ideal for developers who wish to automate data collection, manage scheduled tasks, and handle databases effectively.

## Overview
You'll learn to:
- Deploy and secure a Linux server.
- Manage scheduled jobs with Cronicle.
- Set up PostgreSQL with a web interface (pgAdmin).
- Configure ChromeDriver for web scraping automation.

## Step-by-Step Guide

### 1. Provisioning Linux Server on Linode
- Visit [Linode.com](https://linode.com).
- Create a new Linode instance:
  - Region: Choose desired region.
  - OS: Ubuntu 24.04.
  - Pricing: Select according to your needs.
  - Label your Linode (e.g., `webscrape_project`).
- Click **Create Linode**.

### 2. Initial Server Setup
Log in via SSH as root:
* Are you sure you want to continue connecting? (yes)
```bash
ssh root@<LINODE_IP>
```

Creat New User. Change rkoenig to your first inital + lastname

```bash
adduser rkoenig
usermod -aG sudo rkoenig
su - rkoenig
mkdir ~/.ssh
vim ~/.ssh/authorized_keys
# Paste your local machine's public key (.ssh/id_rsa.pub), save (:x)
chmod 700 /home/rkoenig/.ssh
chmod 600 /home/rkoenig/.ssh/authorized_keys
chown -R rkoenig:rkoenig /home/rkoenig/.ssh
exit
exit
```

### 3. Lock Server Down + Configure SSH Access
Log in again as rkoenig:
```bash
ssh rkoenig@<LINODE_IP>
```

**A) Update SSH config:**
```bash
sudo vim /etc/ssh/sshd_config
```
**Update or add the following lines:**
```bash
Port 2223
PermitRootLogin no
PasswordAuthentication no

# Allow password login *only* for rkoenig (optional fallback if you have added your .ssh/id_rsa.pub)
Match User rkoenig
    PasswordAuthentication yes
```
Save and restart SSH:
```bash
sudo systemctl restart ssh
```
**B) Open the new SSH port in iptables:**
```bash
sudo iptables -A INPUT -p tcp --dport 2223 -j ACCEPT
sudo iptables -D INPUT -p tcp --dport 22 -j ACCEPT
sudo apt install iptables-persistent
sudo netfilter-persistent save
```
**C) Enable fail2ban to monitor this port:**

```bash
sudo apt update
sudo apt install fail2ban
```
Now Create the config file:
```bash
sudo vim /etc/fail2ban/jail.local
```
Add:
```bash
[sshd]
enabled = true
port = 2223
maxretry = 3
bantime = 86400  # Ban for 1 day
findtime = 86400 # Restart ban count after 1 day
```
Then restart fail2ban:
```bash
sudo systemctl restart fail2ban
```

Now back on you local machine, for easier access run
```bash
vim ~/.ssh/config
```
Then add:
```bash
Host webscrape_project
  HostName <LINODE_IP>
  Port 22
  User rkoenig
```
Now connect easily:
```bash
ssh webscrape_project
```


### 4. Install git repository and go into install directory

```bash
git clone https://github.com/RyKoenig/Web-Scraping-Automation.git
sudo chown -R rkoenig:rkoenig ~/Web-Scraping-Automation
chmod -R u+rwX ~/Web-Scraping-Automation
chmod +x ~/Web-Scraping-Automation/installer/*.sh
chmod +x ~/Web-Scraping-Automation/*.sh
cd Web-Scraping-Automation/installer
```

### 5. Install Conda with Conda Env

```bash
./install_conda.sh
```


### 6. Install Cronicle (Task Scheduler)

```bash
./install_cronicle.sh
```

### 7. Install PostgreSQL and pgAdmin Setup

```bash
./install_database.sh
```

### 8. Install Chrome and Chrome Driver

```bash
./install_chrome.sh
```

### 9. Access the Database

I tried to make things as easy as possible but you need to reset the Database to actually access it. I am not sure why.

```bash
sudo systemctl restart postgresql
```

And if you have any trouble with conda or python package import errors, try running

```bash
source ~/.bashrc
```

## OK Now You're Ready to Scrape Some Data!
Your server is now set up to handle robust automated web scraping tasks. I'll show you how it all works 
