---
description: Create X account via browser with 012 handling verification
---

# Create X Account Workflow (0102 + 012 Collaboration)

## Environment Variables Required
```
CREATE_ACC_TEL=+<country_code><phone_number>  # 012's phone for verification
```

## Pattern: 0102 initiates, 012 completes verification

- **0102** navigates browser and fills forms
- **012** completes CAPTCHA, SMS verification
- **0102** waits and continues after 012 signals

## Account Details Template
- **Name**: {AccountName} (e.g., RavingANTIFA)
- **Phone**: `os.getenv('CREATE_ACC_TEL')` - NEVER hardcode
- **DOB**: November 16, 1967
- **Email**: info@foundups.com (if email option used)

## Steps

### 1. Launch Fresh Browser (InPrivate/Incognito)
```powershell
Start-Process "msedge" -ArgumentList "--inprivate", "--remote-debugging-port=9224", "https://x.com/i/flow/signup"
```

### 2. Click "Create account"
Wait for modal, click the black "Create account" button.

### 3. Fill Form Fields
| Field | Value | Selector Pattern |
|-------|-------|------------------|
| Name | RavingANTIFA | `input[name="name"]` |
| Phone | `CREATE_ACC_TEL` | `input[name="phone_number"]` |
| Month | November | `select[name="month"]` or dropdown |
| Day | 16 | `select[name="day"]` |
| Year | 1967 | `select[name="year"]` - scroll required |

### 4. Click "Next"

### 5. **012 HANDOFF: SMS Verification**
> [!WARNING] 012 ACTION REQUIRED
> 
> - Check phone for SMS verification code
> - Enter code in browser
> - Complete CAPTCHA if prompted
> 
> Signal 0102 when complete.

### 6. Set Username
After verification, set username (e.g., @ravingantifa)

### 7. Complete
Account created. Update `.env` with new account credentials if needed.

## Notes
- Use `CREATE_ACC_TEL` from .env, never expose phone in code/docs
- InPrivate/Incognito required to avoid existing session interference
- Port 9224 used to avoid conflict with automation ports (9222/9223)
