#!/usr/bin/env python3
import os
import json
import subprocess
import sys
import getpass

def setup_secretary():
    print("=======================================")
    print("Setting up Secretary Bot environment...")
    print("=======================================")
    
    # Create directories if they don't exist
    directories = ['data', 'files', 'public_files', 'documents']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory already exists: {directory}")
    
    # Setup virtual environment
    if not os.path.exists('venv'):
        print("\nCreating virtual environment...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", "venv"])
            print("✓ Virtual environment created")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create virtual environment: {e}")
            return
    else:
        print("\n✓ Virtual environment already exists")
    
    if os.name == 'nt':  # Windows
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:  # Linux/Mac
        pip_path = os.path.join("venv", "bin", "pip")
    
    if os.path.exists('requirements.txt'):
        print("✓ requirements.txt already exists")
    else:
        print("requirements.txt doesn't exis")
        return 1

    print("\nInstalling required packages from requirements.txt...")
    try:
        subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
        print("✓ Packages installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install packages: {e}")
    
    balance_template = {
        "year": {
            "January": {"balance": 0, "saldo": 0},
            "February": {"balance": 0, "saldo": 0},
            "March": {"balance": 0, "saldo": 0},
            "April": {"balance": 0, "saldo": 0},
            "May": {"balance": 0, "saldo": 0},
            "June": {"balance": 0, "saldo": 0},
            "Jule": {"balance": 0, "saldo": 0},
            "August": {"balance": 0, "saldo": 0},
            "September": {"balance": 0, "saldo": 0},
            "October": {"balance": 0, "saldo": 0},
            "November": {"balance": 0, "saldo": 0},
            "December": {"balance": 0, "saldo": 0}
        },
        "income": [0] * 31,
        "expenses": [0] * 31
    }
    
    tasks_template = {
        "tasks": [],
        "complete": 0
    }
    
    email_html_template = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="x-apple-disable-message-reformatting">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Base</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400&display=swap" em-class="em-font-Inter-Regular">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400&display=swap" em-class="em-font-Inter-Regular">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300&display=swap" em-class="em-font-Inter-Light">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400&display=swap" em-class="em-font-Inter-Regular">
    <style type="text/css">
        html {
            -webkit-text-size-adjust: none;
            -ms-text-size-adjust: none;
        }
    </style>
    <style em="styles">
        .em-font-Inter-Light,.em-font-Inter-Regular {
            font-family: Inter,sans-serif!important;
            font-weight: 300!important;
        }
        .em-font-Inter-Regular {
            font-weight: 400!important;
        }
        @media only screen and (max-device-width:660px),only screen and (max-width:660px) {
            .em-narrow-table {
                width: 100%!important;
                max-width: 660px!important;
                min-width: 320px!important;
            }
            .em-mob-padding_top-0 {
                padding-top: 0!important;
            }
            .em-mob-padding_bottom-0 {
                padding-bottom: 0!important;
            }
            .em-mob-width-100perc {
                width: 100%!important;
                max-width: 100%!important;
            }
            .em-mob-wrap {
                display: block!important;
            }
            .em-mob-padding_right-20 {
                padding-right: 20px!important;
            }
            .em-mob-padding_left-20 {
                padding-left: 20px!important;
            }
        }
    </style>
    <!--[if gte mso 9]>
    <xml>
        <o:OfficeDocumentSettings>
        <o:AllowPNG></o:AllowPNG>
        <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
    </xml>
    <![endif]-->
</head>
<body style="margin: 0px; padding: 0px; background-color: #363636;">
    <span class="preheader" style="visibility: hidden; opacity: 0; color: #363636; height: 0px; width: 0px; font-size: 1px; display: none !important;">&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;</span>
    <!--[if !mso]><!-->
    <div style="font-size:0px;color:transparent;opacity:0;"></div>
    <!--<![endif]-->
    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="font-size: 1px; line-height: normal; background-color: #363636;" bgcolor="#363636">
        <tr em="group">
            <td align="center" style="padding-top: 20px; padding-bottom: 20px;" class="em-mob-padding_top-0 em-mob-padding_bottom-0">
                <!--[if (gte mso 9)|(IE)]>
                <table cellpadding="0" cellspacing="0" border="0" width="660"><tr><td>
                <![endif]-->
                <table cellpadding="0" cellspacing="0" width="100%" border="0" style="max-width: 660px; min-width: 660px; width: 660px;" class="em-narrow-table">
                    <tr em="block" class="em-structure">
                        <td align="center" style="padding: 40px 40px 20px; background-color: #ffffff; background-repeat: repeat;" class="em-mob-padding_left-20 em-mob-padding_right-20" bgcolor="#FFFFFF">
                            <table border="0" cellspacing="0" cellpadding="0" class="em-mob-width-100perc">
                                <tr>
                                    <td width="580" valign="top" class="em-mob-wrap em-mob-width-100perc">
                                        <table cellpadding="0" cellspacing="0" border="0" width="100%" em="atom"><tr><td style="padding: 20px 0 10px;">
                                          <div style="font-family: -apple-system, 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Arial, sans-serif; font-size: 24px; line-height: 32px; color: #1a1a1a;"><strong>Добрый день!<br></strong></div>
                                        </td></tr></table>
                                        <table cellpadding="0" cellspacing="0" border="0" width="100%" em="atom"><tr><td height="20"></td></tr></table>
                                        <table cellpadding="0" cellspacing="0" border="0" width="100%" em="atom">
                                            <tr>
                                                <td style="padding-bottom: 10px;">
                                                    <div style="font-family: Helvetica, Arial, sans-serif; font-size: 16px; line-height: 21px; color: #121212" class="em-font-Inter-Light">{{message}}<br></div>
                                                </td>
                                            </tr>
                                        </table>
                                        <table cellpadding="0" cellspacing="0" border="0" width="100%" em="atom"><tr><td height="20"></td></tr></table>
                                        <table cellpadding="0" cellspacing="0" border="0" width="100%" em="atom"><tr><td style="padding-bottom: 10px;">
                                            <div style="font-family: -apple-system, 'Segoe UI', 'Helvetica Neue', Helvetica, Roboto, Arial, sans-serif; font-size: 16px; line-height: 21px; color: #5a5a5a;">С уважением,<br>Иванущенко Виталий<br></div>
                                        </td></tr></table>
                                        <table cellpadding="0" cellspacing="0" border="0" width="100%" em="atom"><tr><td height="20"></td></tr></table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
                <!--[if (gte mso 9)|(IE)]>
                </td></tr></table>
                <![endif]-->
            </td>
        </tr>
    </table>
</body>
</html>"""
    
    print("\nCreating template files...")
    templates = {
        'data/balance.json': balance_template,
        'data/tasks.json': tasks_template
    }
    
    for file_path, template in templates.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=4, ensure_ascii=False)
            print(f"✓ Created file: {file_path}")
        else:
            print(f"✓ File already exists: {file_path}")
    
    email_path = 'data/email.html'
    if not os.path.exists(email_path):
        with open(email_path, 'w', encoding='utf-8') as f:
            f.write(email_html_template)
        print(f"✓ Created file: {email_path}")
    else:
        print(f"✓ File already exists: {email_path}")
    
    # Create .env file with required variables
    print("\nSetting up environment variables...")
    env_path = '.env'
    if not os.path.exists(env_path):
        print("Please provide the following information for your bot:")
        bot_token = input("Telegram Bot Token: ")
        user_id = input("Your Telegram User ID: ")
        email_address = input("Email Address: ")
        email_password = getpass.getpass("Email Password: ")
        smtp_address = input("SMTP Server Address (default smtp.gmail.com): ") or "smtp.gmail.com"
        imap_address = input("IMAP Server Address (default imap.gmail.com): ") or "imap.gmail.com"
        vps_user_stats = input("VPS User Stats URL: ")
        
        env_content = f"""# Bot Configuration
            BOT_TOKEN={bot_token}
            USER_ID={user_id}

            # Email Configuration
            EMAIL_ADDRESS={email_address}
            EMAIL_PASSWORD={email_password}
            SMTP_ADDRESS={smtp_address}
            IMAP_ADDRESS={imap_address}

            # VPS Configuration
            VPS_USER_STATS={vps_user_stats}
            """
        
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✓ Created .env file")
    else:
        print(f"✓ .env file already exists")

    if os.name != 'nt':
        print("\nSetting up systemd service...")
        import platform
        if platform.system() == "Linux":
            install_service = input("Do you want to install the secretary.service for automatic startup? (y/n): ").lower()
            if install_service == 'y' or install_service == 'yes':
                current_path = os.path.abspath('.')
                venv_path = os.path.join(current_path, "venv", "bin", "python3")
                main_script_path = os.path.join(current_path, "main.py")

                service_content = f"""[Unit]
                    Description=secretary
                    After=multi-user.target

                    [Service]
                    User={os.getlogin()}
                    Group={os.getlogin()}
                    Type=simple
                    Restart=always
                    ExecStart={venv_path} {main_script_path}

                    [Install]
                    WantedBy=multi-user.target
                    """

                with open('secretary.service', 'w') as f:
                    f.write(service_content)
                print("✓ Created secretary.service file")

                print("Installing service (requires sudo)...")
                try:
                    subprocess.check_call(['sudo', 'cp', 'secretary.service', '/etc/systemd/system/'])
                    subprocess.check_call(['sudo', 'systemctl', 'daemon-reload'])
                    subprocess.check_call(['sudo', 'systemctl', 'enable', 'secretary.service'])
                    subprocess.check_call(['sudo', 'systemctl', 'start', 'secretary.service'])
                    print("✓ Service installed and started successfully")
                    print("\nService status:")
                    subprocess.call(['sudo', 'systemctl', 'status', 'secretary.service'])
                except subprocess.CalledProcessError as e:
                    print(f"✗ Failed to install service: {e}")
                    print("You can install it manually with:")
                    print(f"  sudo cp secretary.service /etc/systemd/system/")
                    print(f"  sudo systemctl daemon-reload")
                    print(f"  sudo systemctl enable secretary.service")
                    print(f"  sudo systemctl start secretary.service")
            else:
                print("Skipping service installation")
                print("\nYou can install the service manually later by:")
                print(f"  sudo cp secretary.service /etc/systemd/system/")
                print(f"  sudo systemctl daemon-reload")
                print(f"  sudo systemctl enable secretary.service")
                print(f"  sudo systemctl start secretary.service")
    
    print("\n=======================================")
    print("✓ Secretary Bot setup complete!")
    print("=======================================")
    print("\nTo start the bot:")
    if os.name == 'nt':  # Windows
        print("- Activate the virtual environment: .\\venv\\Scripts\\activate")
    else:  # Linux/Mac
        print("- Activate the virtual environment: source venv/bin/activate")
    print("- Run the bot: python main.py")
    print("=======================================")

if __name__ == "__main__":
    setup_secretary()