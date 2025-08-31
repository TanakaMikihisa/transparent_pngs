import os
import shutil
from PIL import Image, ImageFilter
from pathlib import Path

def make_transparent_pil(input_path, output_path):
    try:
        print(f"PIL高精度処理開始: {os.path.basename(input_path)}")
        
        # 画像を開く
        with Image.open(input_path) as img:
            # RGBAモードに変換
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 画像データを取得
            data = img.getdata()
            width, height = img.size
            
            # 新しい画像データを作成
            new_data = []
            
            # 透過処理
            for y in range(height):
                for x in range(width):
                    idx = y * width + x
                    r, g, b, a = data[idx]
                    
                    # 白色度を計算（RGB値の平均）
                    white_ratio = (r + g + b) / 3.0
                    
                    # より厳密な白色判定
                    if white_ratio >= 240 and abs(r - g) < 10 and abs(g - b) < 10 and abs(r - b) < 10:
                        # ほぼ完全な白色の場合、完全に透明
                        new_alpha = 0
                    elif white_ratio >= 220 and abs(r - g) < 15 and abs(g - b) < 15 and abs(r - b) < 15:
                        # 薄い白色の場合、部分的に透明
                        ratio = (white_ratio - 220) / (240 - 220)
                        new_alpha = int(255 * (1.0 - ratio))
                    else:
                        # その他の色は不透明
                        new_alpha = 255
                    
                    # 新しいピクセルデータを追加
                    new_data.append((r, g, b, new_alpha))
            
            # 新しい画像を作成
            new_img = Image.new('RGBA', img.size)
            new_img.putdata(new_data)
            
            # エッジを滑らかにする（軽い処理）
            # アルファチャンネルのみに軽いブラーを適用
            alpha_channel = new_img.split()[-1]
            smoothed_alpha = alpha_channel.filter(ImageFilter.GaussianBlur(radius=0.3))
            
            # 最終画像を作成
            r, g, b, _ = new_img.split()
            final_img = Image.merge('RGBA', (r, g, b, smoothed_alpha))
            
            # 高品質で保存
            final_img.save(output_path, 'PNG', optimize=True, compress_level=9)
            
            print(f"✅ PIL高精度透過完了: {os.path.basename(input_path)}")
            
    except Exception as e:
        print(f"❌ PIL処理エラー: {input_path} - {str(e)}")
        raise

def process_pngs():
    """
    original_pngsフォルダ内のPNG画像を処理する
    """
    # パスの設定
    original_dir = Path("original_pngs")
    used_dir = Path("used_pngs")
    
    # ディレクトリが存在しない場合は作成
    original_dir.mkdir(exist_ok=True)
    used_dir.mkdir(exist_ok=True)
    
    # PNGファイルを検索
    png_files = list(original_dir.glob("*.png"))
    
    if not png_files:
        print("original_pngsフォルダにPNGファイルが見つかりませんでした。")
        return
    
    print(f"処理対象のPNGファイル数: {len(png_files)}")
    print("PIL高精度透過処理を開始します...")
    
    for png_file in png_files:
        try:
            print(f"\n{'='*60}")
            print(f"🎯 {png_file.name} を高精度処理中...")
            print(f"{'='*60}")
            
            # 1. 元のファイルをused_pngsにコピー
            used_path = used_dir / png_file.name
            print(f"📋 元ファイルをコピー: {used_path}")
            shutil.copy2(str(png_file), str(used_path))
            
            # 2. PIL高精度透過処理を実行
            temp_output = original_dir / f"temp_{png_file.name}"
            print(f"🔬 PIL高精度処理実行: {temp_output}")
            make_transparent_pil(str(png_file), str(temp_output))
            
            # 3. 元のファイルを削除
            print(f"🗑️ 元ファイル削除: {png_file}")
            os.remove(str(png_file))
            
            # 4. 透過された画像を最終保存
            final_output = original_dir / png_file.name
            print(f"💾 最終保存: {final_output}")
            shutil.move(str(temp_output), str(final_output))
            
            print(f"🎉 高精度処理完了: {png_file.name}")
            
        except Exception as e:
            print(f"❌ エラー: {png_file.name} - {str(e)}")
            # エラーが発生した場合、元のファイルを復元
            try:
                if os.path.exists(str(used_path)):
                    shutil.copy2(str(used_path), str(png_file))
                    print(f"🔄 元ファイルを復元しました: {png_file.name}")
            except:
                print(f"⚠️ 元ファイルの復元に失敗しました: {png_file.name}")
    
    print(f"\n{'='*60}")
    print("🎯 すべての高精度透過処理が完了しました！")
    print(f"{'='*60}")

def main():
    """
    メイン関数
    """
    print("🚀 PIL高精度PNG画像透過処理を開始します...")
    print("=" * 60)
    print("🔬 使用技術:")
    print("  • PIL (Pillow) 精密画像処理")
    print("  • 厳密な白色判定アルゴリズム")
    print("  • 軽量エッジ滑らか化処理")
    print("  • 高品質PNG保存")
    print("=" * 60)
    
    try:
        process_pngs()
    except KeyboardInterrupt:
        print("\n⚠️ 処理が中断されました。")
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {str(e)}")
    
    print("=" * 60)
    print("🏁 処理が終了しました。")

if __name__ == "__main__":
    main()
