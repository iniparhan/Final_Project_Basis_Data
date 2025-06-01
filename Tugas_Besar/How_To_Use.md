# Gimana sih make ini?

## Problem

- waktu running `app.py` masih nampilin `Not Found`, perlu ada perbaikan 
- di `http://127.0.0.1:5000/dashboard` masih nampilin `"message": "Token is missing!"`, perlu ada perbaikan 
- waktu running `dashboard.html`, cuma nampilin header, harusnya banyak data, perlu perbaikan
- udah, itu doang si, sisa pengujian performa query SQL pake  SQLQueryStress aja


## Struktur Folder

```
/project-root
├── app.py           # File utama aplikasi Flask / Backend Flask server
├── dashboard.html   # Template halaman dashboard untuk admin / Halaman frontend dashboard
├── get_token.py     # Script untuk mendapatkan token JWT / Script untuk ambil token JWT (untuk autentikasi)
├── locust_file.py   # Script untuk load testing menggunakan Locust / Script load testing untuk simulasi user
├── database         #  Databases
```

---

## Cara Menjalankan Project

1. **Clone repository**

   ```
   git clone https://github.com/iniparhan/Final_Project_Basis_Data.git
   cd repository
   ```

   Kalo gak bisa, manual ae wes di download
   
   akwoakwoak

2. **Install dependencies**

   Pastikan Python sudah terinstall, lalu install package yang dibutuhkan:

    Caranya?

    Buka dulu terminal atau `cmd`, trus copy paste syntax dibawah ini:
   ```
   pip install flask mysql-connector-python pyjwt locust
   ```

3. **Jalankan database MySQL**
    
    Sebelumnya download dulu database yang sudah kubuat, ini linknya [database](https://drive.google.com/file/d/1gKOWsossYEnTNNyc73mQHbdJ5Bz_aoGC/view?usp=sharing), pastikan MySQL server sudah berjalan dan database sudah siap yo rek.

4. **Jalankan aplikasi Flask**

    Kalo nge run saranku pake terminal external, jangan dari vs code

    pastiin udah di direktori atau file code tempat nyimpan file e yo rek, trus copy paste syntax dibawah :

   ```
   python app.py
   ```

   Aplikasi akan berjalan di `http://127.0.0.1:5000`

5. **Dapatkan Token JWT**

    Nah, yang `app.py` ini biarin aja nge-run di terminal itu, buka terminal baru lagi, trus run script ini untuk mendapatkan token login:

   ```
   python get_token.py
   ```

   nanti di terminal bakal munculin token nya.

   copy tokennya, terus masukkin ke `dashboard.html` sama `locust_file.py`

   keliatan kok ada variabel `TOKEN` disitu

6. **Buka Dashboard**

   Buka browser dan akses:

   ```
   http://127.0.0.1:5000/
   ```

   Gunakan token JWT yang didapat dari langkah sebelumnya.

7. **Menjalankan Load Test dengan Locust**

   Jalankan syntax ini di terminal:

   ```
   python -m locust -f locust_file.py --host=http://127.0.0.1:5000
   ```

   Buka `http://localhost:8089` di browser untuk konfigurasi dan mulai testing.

