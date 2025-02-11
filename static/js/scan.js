const video = document.getElementById('video');

//カメラを起動
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;

        //自動で書類を検出する処理
        setTimeout(() => {
            alert("書類が検出されました。スキャンを開始します。");
            //サーバーに画像を送信してscan_result.htmlに遷移
            window.location.href = "/scan_result";
        }, 5000); //仮に5秒後に自動でスキャン完了とする
    })
    .catch(error => {
        console.error("カメラの起動に失敗しました:", error);
    });
