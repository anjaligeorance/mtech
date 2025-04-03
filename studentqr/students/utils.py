import qrcode
import numpy as np
from PIL import Image
import os
from django.conf import settings
import uuid

def generate_qr_code(data):
    """Generate QR code from data"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    return qr_img

def visual_cryptography_encrypt(image):
    """
    Encrypt an image using visual cryptography (2,2) scheme
    Returns two shares that need to be overlaid to recover the original
    """
    # Convert to numpy array
    img_array = np.array(image.convert('1'))
    height, width = img_array.shape
    
    # Initialize shares
    share1 = np.zeros((height*2, width*2), dtype=np.uint8)
    share2 = np.zeros((height*2, width*2), dtype=np.uint8)
    
    # Patterns for white and black pixels
    patterns = [
        [[[1, 0], [0, 1]], [[0, 1], [1, 0]]],  # White pixel
        [[[1, 0], [0, 1]], [[1, 0], [0, 1]]]   # Black pixel
    ]
    
    # Generate shares
    for i in range(height):
        for j in range(width):
            # Determine pattern based on pixel value (0=black, 255=white)
            pattern_idx = 0 if img_array[i, j] > 0 else 1
            
            # Randomly select one of the two possible patterns
            pattern_choice = np.random.randint(0, 2)
            
            # Apply pattern to shares
            p1 = patterns[pattern_idx][pattern_choice]
            
            if pattern_idx == 0:  # White pixel
                p2 = patterns[0][1-pattern_choice]
            else:  # Black pixel
                p2 = patterns[1][0]  # For black, we use the same pattern
            
            # Set 2x2 section in each share
            share1[i*2:i*2+2, j*2:j*2+2] = p1
            share2[i*2:i*2+2, j*2:j*2+2] = p2
    
    # Convert to PIL images
    share1_img = Image.fromarray(share1 * 255)
    share2_img = Image.fromarray(share2 * 255)
    
    return share1_img, share2_img

def visual_cryptography_decrypt(share1, share2):
    """
    Decrypt by overlaying the two shares
    """
    # Open shares if filenames are provided
    if isinstance(share1, str):
        share1 = Image.open(share1).convert('1')
    if isinstance(share2, str):
        share2 = Image.open(share2).convert('1')
    
    # Convert to numpy arrays
    s1_array = np.array(share1)
    s2_array = np.array(share2)
    
    # Overlay shares using logical AND operation
    # In visual cryptography, a black pixel is represented by 0
    # and a white pixel is represented by 1
    result_array = np.logical_and(s1_array, s2_array).astype(np.uint8) * 255
    
    # Convert back to PIL image
    result_img = Image.fromarray(result_array)
    
    return result_img

def process_student_qr(student):
    """Generate QR code and encrypt it for a student"""
    # Create QR code with student info
    qr_data = f"ID: {student.id}\nName: {student.name}\nClass: {student.class_name}\nRoll: {student.roll_number}"
    qr_img = generate_qr_code(qr_data)
    
    # Save QR code
    qr_path = os.path.join('qr_codes', f"{student.id}.png")
    full_qr_path = os.path.join(settings.MEDIA_ROOT, qr_path)
    os.makedirs(os.path.dirname(full_qr_path), exist_ok=True)
    qr_img.save(full_qr_path)
    
    # Encrypt QR code using visual cryptography
    share1_img, share2_img = visual_cryptography_encrypt(qr_img)
    
    # Save shares
    share1_path = os.path.join('shares', f"{student.id}_share1.png")
    share2_path = os.path.join('shares', f"{student.id}_share2.png")
    
    full_share1_path = os.path.join(settings.MEDIA_ROOT, share1_path)
    full_share2_path = os.path.join(settings.MEDIA_ROOT, share2_path)
    
    os.makedirs(os.path.dirname(full_share1_path), exist_ok=True)
    
    share1_img.save(full_share1_path)
    share2_img.save(full_share2_path)
    
    # Update student record
    student.qr_code = qr_path
    student.share1 = share1_path
    student.share2 = share2_path
    student.save()
    
    return qr_path, share1_path, share2_path
