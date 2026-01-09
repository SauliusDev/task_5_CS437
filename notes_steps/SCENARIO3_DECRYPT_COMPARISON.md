# Scenario 3: Decrypt-Then-Scan Implementation

## Summary

✅ **The decrypt endpoint with scanning after decryption is ALREADY IMPLEMENTED in the patched version!**

## Key Difference: Vulnerable vs Patched

### 🔴 Vulnerable Version (Lines 212-245)

```python
@upload_bp.route('/upload/scenario3/decrypt/<int:file_id>', methods=['POST'])
@admin_required
def decrypt_file(file_id):
    # ... get encrypted file ...
    
    # Decrypt
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    decrypted_content = unpad(cipher.decrypt(encrypted_content), AES.block_size)
    
    # ❌ NO SCANNING AFTER DECRYPTION - This is the vulnerability!
    
    # Directly save to disk
    decrypted_filename = f"decrypted_{upload['original_filename']}"
    decrypted_path = os.path.join(UPLOAD_FOLDER, 'firmware', decrypted_filename)
    
    with open(decrypted_path, 'wb') as f:
        f.write(decrypted_content)
    
    flash(f'File decrypted successfully: {decrypted_filename}', 'success')
```

**Problem:** Malicious content hidden in encryption bypasses scanning!

---

### ✅ Patched Version (Lines 169-237)

```python
@upload_bp.route('/upload/encrypted/decrypt/<int:file_id>', methods=['POST'])
@admin_required
def decrypt_file(file_id):
    # ... get encrypted file ...
    
    # Decrypt
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    decrypted_content = unpad(cipher.decrypt(encrypted_content), AES.block_size)
    
    # ✅ SECURITY FIX: Scan AFTER decryption (decrypt-then-scan pipeline)
    
    # 1. Check for malicious patterns
    malicious_patterns = [b'<?php', b'<script', b'<iframe', b'eval(', b'exec(']
    for pattern in malicious_patterns:
        if pattern in decrypted_content:
            flash('Malicious content detected after decryption - file blocked', 'danger')
            return redirect(url_for('upload.upload_index'))
    
    # 2. Verify file type using magic bytes
    if MAGIC_AVAILABLE:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(decrypted_content)
        
        allowed_mime_types = [
            'application/octet-stream',
            'text/plain',
            'application/x-executable'
        ]
        
        if mime_type not in allowed_mime_types:
            flash(f'Invalid file type after decryption: {mime_type} - file blocked', 'danger')
            return redirect(url_for('upload.upload_index'))
    
    # 3. Size check after decryption
    if len(decrypted_content) > MAX_FILE_SIZE:
        flash('Decrypted file exceeds size limit', 'danger')
        return redirect(url_for('upload.upload_index'))
    
    # 4. Only save if all checks pass
    decrypted_filename = f"{secrets.token_hex(16)}_{upload['original_filename']}"
    decrypted_path = os.path.join(UPLOAD_FOLDER, 'firmware', decrypted_filename)
    
    with open(decrypted_path, 'wb') as f:
        f.write(decrypted_content)
    
    flash(f'File decrypted successfully after security verification', 'success')
```

**Solution:** Three-layer security check AFTER decryption!

---

## The Pipeline Design Flaw Explained

### ❌ Vulnerable Pipeline
```
Upload → Scan (on plaintext) → Encrypt → Store → Decrypt → Save (NO SCAN!)
                                                              ↑
                                                      VULNERABILITY HERE
```

**Problem:** Scanning happens BEFORE encryption. After decryption, no re-scan occurs.

**Attack:** Attacker uploads malicious file, it gets scanned (clean), encrypted, stored. Later, when decrypted, malicious content is extracted without re-scanning.

### ✅ Patched Pipeline
```
Upload → Scan → Encrypt → Store → Decrypt → Scan Again → Save
                                              ↑
                                         FIX HERE!
```

**Solution:** Decrypt-then-scan ensures malicious content is detected even if hidden through encryption.

---

## For Your Report

### Section 4.1.3: CWE-434 Scenario 3 - Encrypted Bypass

**Vulnerability Description:**
> "The third scenario demonstrates a pipeline design flaw. The server scans files before encryption but does not re-scan after decryption. This allows attackers to bypass content scanning by hiding malicious payloads inside encrypted files. When the file is later decrypted, the malicious content is extracted without security verification."

**Exploitation Steps:**
1. Upload a malicious file (e.g., containing `<?php system($_GET['cmd']); ?>`)
2. File is scanned on plaintext (before encryption) - passes if disguised
3. File is encrypted with AES-256-CBC
4. File is stored as `.enc`
5. Attacker triggers decryption via `/upload/scenario3/decrypt/<id>`
6. Vulnerable version extracts malicious file WITHOUT re-scanning
7. Malicious content now accessible in `uploads/firmware/`

**Monitoring:** All upload and decrypt attempts are logged in the monitoring system.

### Section 6.1.3: CWE-434 Scenario 3 - Patch

**Changes Made:**
1. **Decrypt-then-scan pipeline:** Scanning occurs AFTER decryption, not just before encryption
2. **Pattern matching:** Checks for common malicious patterns (`<?php`, `<script>`, `eval(`, etc.)
3. **Magic byte verification:** Validates file type on decrypted content
4. **Size verification:** Ensures decrypted content doesn't exceed limits
5. **Secure filename:** Uses random token for decrypted files

**Why It Works:**
> "The patched version implements a proper decrypt-then-scan pipeline. Even if malicious content is hidden through encryption and bypasses the initial scan, it will be detected when the file is decrypted. This closes the security gap by ensuring all plaintext content is validated before being saved to disk."

**Verification:**
- Upload encrypted malicious file on vulnerable version → decrypts successfully ❌
- Upload same file on patched version → decryption blocked after scan ✅
- Monitoring logs show both attempts with outcome "allowed" vs "blocked"

---

## Testing Notes

**To demonstrate this vulnerability:**

1. **Create malicious file:**
   ```bash
   echo '<?php system($_GET["cmd"]); ?>' > malicious.php
   ```

2. **Upload to vulnerable `/upload/scenario3`**
   - File encrypted and stored

3. **Trigger decrypt on vulnerable version**
   - POST to `/upload/scenario3/decrypt/<id>`
   - File extracted WITHOUT scanning
   - Malicious PHP file now in firmware folder

4. **Try same on patched version**
   - POST to `/upload/encrypted/decrypt/<id>`
   - Scanning detects `<?php` pattern
   - Decryption blocked with error message
   - No file saved

5. **Check monitoring dashboard**
   - Vulnerable: Shows decrypt as "allowed"
   - Patched: Shows decrypt as "blocked"

---

## Endpoint Differences

| Aspect | Vulnerable | Patched |
|--------|-----------|---------|
| Upload endpoint | `/upload/scenario3` | `/upload/encrypted` |
| Decrypt endpoint | `/upload/scenario3/decrypt/<id>` | `/upload/encrypted/decrypt/<id>` |
| Scanning after decrypt | ❌ No | ✅ Yes |
| Pattern matching | ❌ No | ✅ Yes (5 patterns) |
| Magic byte check | ❌ No | ✅ Yes |
| Size verification | ❌ No | ✅ Yes |
| Filename security | Predictable | Random token |

---

## Summary

✅ **Implementation is complete and correct!**

The patched version properly implements the decrypt-then-scan pipeline, demonstrating understanding of the security principle that the professor is testing. This is superior to simply removing the decryption feature, as it:

1. Preserves legitimate functionality
2. Demonstrates proper secure design
3. Shows understanding of the pipeline flaw
4. Implements defense in depth

**For your report:** Use the code comparison above and explain the pipeline design flaw clearly. This is a strong implementation that meets the assignment requirements.
