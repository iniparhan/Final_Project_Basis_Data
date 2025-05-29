# With Laravel

## 1. LARAVEL PROJECT SETUP

### A. Create Laravel Project (in terminal):

```bash
composer create-project laravel/laravel rbac-dashboard
cd rbac-dashboard
```

---

## 2. INSTALL AUTH + RBAC

### A. Laravel Breeze (for Auth)

```bash
composer require laravel/breeze --dev
php artisan breeze:install
npm install && npm run dev
php artisan migrate
```

---

## 3. CREATE ROLES SYSTEM

### A. Migration for Roles

```bash
php artisan make:migration create_roles_table
```

#### `database/migrations/xxxx_create_roles_table.php`

```php
public function up()
{
    Schema::create('roles', function (Blueprint $table) {
        $table->id();
        $table->string('name');
        $table->timestamps();
    });

    Schema::table('users', function (Blueprint $table) {
        $table->foreignId('role_id')->nullable()->constrained('roles');
    });
}
```

### B. Seeder for Roles and Admin User

```bash
php artisan make:seeder RoleSeeder
php artisan make:seeder UserSeeder
```

#### `database/seeders/RoleSeeder.php`

```php
use Illuminate\Support\Facades\DB;

DB::table('roles')->insert([
    ['name' => 'admin'],
    ['name' => 'user'],
    ['name' => 'manager']
]);
```

#### `database/seeders/UserSeeder.php`

```php
use App\Models\User;

User::create([
    'name' => 'Admin',
    'email' => 'admin@example.com',
    'password' => bcrypt('password'),
    'role_id' => 1
]);
```

```bash
php artisan db:seed --class=RoleSeeder
php artisan db:seed --class=UserSeeder
```

---

## 4. MIDDLEWARE RBAC

### A. Create Middleware

```bash
php artisan make:middleware RoleMiddleware
```

#### `app/Http/Middleware/RoleMiddleware.php`

```php
public function handle($request, Closure $next, ...$roles)
{
    if (!$request->user() || !in_array($request->user()->role->name, $roles)) {
        abort(403, 'Unauthorized');
    }
    return $next($request);
}
```

### B. Register Middleware

In `app/Http/Kernel.php`:

```php
'role' => \App\Http\Middleware\RoleMiddleware::class,
```

---

## 📊 5. ADMIN DASHBOARD + ROUTE

### A. Route

In `routes/web.php`:

```php
use App\Http\Controllers\DashboardController;

Route::middleware(['auth', 'role:admin'])->group(function () {
    Route::get('/admin/dashboard', [DashboardController::class, 'index']);
    Route::get('/api/data', [DashboardController::class, 'getData']);
});
```

### B. Controller

```bash
php artisan make:controller DashboardController
```

#### `app/Http/Controllers/DashboardController.php`

```php
use Illuminate\Support\Facades\DB;

class DashboardController extends Controller
{
    public function index()
    {
        return view('admin.dashboard');
    }

    public function getData()
    {
        $data = DB::table('large_table')->limit(1000)->get();
        return response()->json(['data' => $data]);
    }
}
```

---

## 🧾 6. FRONTEND (View)

### `resources/views/admin/dashboard.blade.php`

```blade
@extends('layouts.app')

@section('content')
<div class="container">
    <h2>Dashboard</h2>
    <table id="data-table" class="table">
        <thead>
            <tr>
                <th>ID</th><th>Name</th><th>Value</th>
            </tr>
        </thead>
    </table>
</div>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.5/css/jquery.dataTables.min.css">
<script src="https://cdn.datatables.net/1.13.5/js/jquery.dataTables.min.js"></script>

<script>
$(document).ready(function () {
    $('#data-table').DataTable({
        ajax: '/api/data',
        columns: [
            { data: 'id' },
            { data: 'name' },
            { data: 'value' }
        ]
    });
});
</script>
@endsection
```

---

## 💾 7. LARGE TABLE (DATABASE + SEEDER)

### A. Create Table

```bash
php artisan make:migration create_large_table
```

#### `database/migrations/xxxx_create_large_table.php`

```php
Schema::create('large_table', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->integer('value');
    $table->timestamps();
});
```

### B. Seeder

```bash
php artisan make:seeder LargeTableSeeder
```

#### `database/seeders/LargeTableSeeder.php`

```php
use Illuminate\Support\Facades\DB;

for ($i = 0; $i < 500000; $i++) {
    DB::table('large_table')->insert([
        'name' => 'Item ' . $i,
        'value' => rand(1, 1000),
        'created_at' => now(),
        'updated_at' => now(),
    ]);
}
```

```bash
php artisan migrate
php artisan db:seed --class=LargeTableSeeder
```

---

## 🔥 8. LOCUST STRESS TEST SCRIPT (locustfile.py)

```python
from locust import HttpUser, task, between

class DashboardUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def load_dashboard_data(self):
        self.client.get("/api/data")
```

```bash
locust -f locustfile.py --host=http://localhost:8000
```

---

## 📈 9. SQL QUERY STRESS TEST (Python)

```python
import mysql.connector, time

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="rbac_dashboard"
)

cursor = conn.cursor()
query = "SELECT * FROM large_table LIMIT 1000"

start = time.time()
for _ in range(1000):
    cursor.execute(query)
    cursor.fetchall()
end = time.time()

print(f"Elapsed Time: {end - start:.2f}s")
```

---

## ✅ PROJECT STRUCTURE OVERVIEW

```
rbac-dashboard/
├── app/
│   ├── Http/
│   │   ├── Controllers/DashboardController.php
│   │   └── Middleware/RoleMiddleware.php
├── database/
│   ├── migrations/create_large_table.php
│   └── seeders/{RoleSeeder, UserSeeder, LargeTableSeeder}.php
├── resources/views/admin/dashboard.blade.php
├── routes/web.php
```

## ✅ **PROJECT CRITERIA CHECKLIST**

| Kriteria                                    | Status    | Penjelasan                                                                |
| ------------------------------------------- | --------- | ------------------------------------------------------------------------- |
| **Tech stack bebas**                        | ✅         | Laravel (backend), Blade + jQuery (frontend), MySQL/PostgreSQL (database) |
| **Database dengan >500.000 row per tabel**  | ✅         | Seeder `LargeTableSeeder` mengisi 500.000+ row                            |
| **Autentikasi** (login)                     | ✅         | Laravel Breeze                                                            |
| **RBAC (Role-Based Access Control)**        | ✅         | Middleware `RoleMiddleware` dan relasi `users.role_id → roles.id`         |
| **Dashboard admin** dengan tabel data       | ✅         | Halaman `/admin/dashboard` + AJAX `/api/data` pakai DataTables            |
| **Stress test halaman dashboard**           | ✅         | Disiapkan file `locustfile.py` untuk uji akses halaman                    |
| Uji **dengan dan tanpa pagination**         | ✅         | DataTables di frontend dapat dimodif untuk pakai pagination / full dump   |
| **Uji variasi jumlah user** (10, 100, 1000) | ✅         | Locust mendukung ini dengan `--users` parameter saat dijalankan           |
| **Stress test query SQL**                   | ✅         | Python script untuk uji query 1000x                                       |
| Uji dengan **variasi iterasi dan thread**   | ✅         | Script Python bisa dimodif untuk thread/loop                              |
| **Optimasi query dan bandingkan hasilnya**  | ⚠️ Manual | Harus kamu tambahkan sendiri, misalnya index atau limit lebih sempit      |

---

## Untuk memenuhi bagian terakhir:

> “**Optimalkan query tersebut dan bandingkan hasil pengujian sebelum dan sesudah optimasi**”

1. Jalankan query asli (tanpa index).
2. Tambahkan index di kolom `name` atau `value`:

   ```sql
   CREATE INDEX idx_name ON large_table(name);
   ```
3. Ulangi stress test SQL script dan bandingkan waktu sebelum dan sesudah.
4. Masukkan grafik (misalnya dari Excel) ke laporan PDF kamu.

