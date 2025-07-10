# Maintainer: Saeed Badrelden <saeedbadrelden2021@gmail.com>
pkgname=hel-diagram
pkgver=1.0.0
pkgrel=1
pkgdesc="A GUI tool to generate and build directory structure diagrams - Helwan Linux Project"
arch=('any')
url="https://github.com/helwan-linux/hel-diagram-builder"
license=('MIT')
depends=('python' 'python-pyqt5' 'python-watchdog')
makedepends=('git')
source=("git+https://github.com/helwan-linux/hel-diagram-builder.git")
md5sums=('SKIP')

build() {
  echo "Nothing to build."
}

package() {
  cd "$srcdir/hel-diagram-builder"

  install -d "$pkgdir/opt/$pkgname"
  cp -r hel-diagram/* "$pkgdir/opt/$pkgname/"

  # إنشاء مشغل (launcher)
  install -Dm755 /dev/stdin "$pkgdir/usr/bin/$pkgname" <<EOF
#!/bin/bash
cd /opt/$pkgname
exec python3 main.py "\$@"
EOF

  # أيقونة وملف desktop
  install -Dm644 hel-diagram/gui/icon.png "$pkgdir/usr/share/pixmaps/$pkgname.png"
  install -Dm644 hel-diagram/hel-diagram.desktop "$pkgdir/usr/share/applications/$pkgname.desktop"
}
