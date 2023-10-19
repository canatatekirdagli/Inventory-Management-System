# Inventory Management System
 This project is a Python-based Inventory Tracking System that processes transaction data, parses it and stores it in a SQLite database.

## Kullanım

### Gereksinimlerin Kurulumu

Script'in çalışabilmesi için Python yüklü olmalıdır. Ayrıca, gerekli Python modüllerinin yüklü olduğundan emin olun. Gereksinimleri yüklemek için terminal veya komut istemcisinden yükleyebilirsiniz.

### Veri Dosyasını Hazırlama

1. Projenizin ana dizininde `txt` adında bir klasör oluşturun (eğer yoksa).
2. Bu klasörün içine `firstData.txt` adında bir veri dosyası oluşturun veya mevcut bir veri dosyasını bu adrese yerleştirin. Veri dosyasının her satırı, belirli bir yapıya sahip olmalıdır.

   Örnek veri yapısı:

   ```plaintext
   1244194,2023-09-16 00:00:16,COMPLETED,4326698,STOCK_PRICE_UPDATE,[{"qty": 31, "sku": "4326698-4009209352015", "price": null, "discountedPrice": null}, {"qty": 87, "sku": "4326698-8681734439315", "price": null, "discountedPrice": null}]
   ```
3. Script'i çalıştırma
Script'i çalıştırmak için terminal veya komut istemcisinde aşağıdaki komutu çalıştırın:
```bash
python txt/main.py
```
Script, veri dosyasını işleyecek, veritabanına kaydedecek, sonuçları analiz edecek ve dosyaya yazacaktır.
4. Sonuçları Kontrol Etme
Script çalıştırıldıktan sonra, sonuç dosyalarını txt/ dizininde bulabilirsiniz:
-sorted.txt: SKU'lere göre sıralanmış değişiklikler
-unchanged_products.txt: Değişmeyen ürünlerin listesi

### Hata Durumları
- **FileNotFoundError**: Belirtilen veri dosyası bulunamadığında ortaya çıkar. 
- **ValueError**: Veri yapısının beklenen formatta olmadığında ortaya çıkar. 
- **JSONDecodeError**: JSON verisi doğru şekilde ayrıştırılamadığında ortaya çıkar.
  
### Notlar
- Script çalıştırıldığında, her aşamanın durumu ekrana yazdırılır.
