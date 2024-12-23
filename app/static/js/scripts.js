// 動畫控制代碼
document.addEventListener('DOMContentLoaded', () => {
    const animation = document.getElementById('my-animation');
    const giftContainer = document.getElementById('gift-container');
    const awardTable = document.getElementById('award-table');
    const isGiftDrawn = giftContainer.getAttribute('data-gift-drawn');
    const giftId = giftContainer.getAttribute('data-gift-id');

    // 動態填充得獎名單
    fetch(`/winners_fragment/${giftId}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('award-table').innerHTML = html;

            const reassignButtons = document.querySelectorAll('.reassign-btn');
            bindRedrawEvent(reassignButtons);
        })
        .catch(error => console.error('Error loading winners fragment:', error));

    if (isGiftDrawn === '0') {
        // 設置 GIF 播放完成後的處理
        animation.addEventListener('load', () => {
            console.log('GIF loaded');

            // 設置 GIF 播放完成後的處理
            setTimeout(() => {
                console.log('GIF completed');

                // 顯示禮物容器
                giftContainer.style.display = 'flex';
                animation.style.display = 'none';
                awardTable.style.display = 'flex';
            }, 3750); // 假設 GIF 播放時間為 5 秒
        });
        if (animation.complete) {
            animation.dispatchEvent(new Event('load'));
        }
    } else {
        // 顯示禮物容器
        giftContainer.style.display = 'flex';
        animation.style.display = 'none';
        awardTable.style.display = 'flex';
    }

});


function bindRedrawEvent(container) {
    // 在更新內容後，綁定新的重抽按鈕事件
    container.forEach(button => {
        button.addEventListener('click', function () {
            const employeeCode = this.getAttribute('data-employee-code');
            const giftId = this.getAttribute('data-gift-id');

            fetch('/redraw', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    employee_code: employeeCode,
                    gift_id: giftId
                })
            })
                .then(response => response.json())
                .then(async data => {
                    if (data.success) {

                        // 執行成功後，重新載入得獎者清單並綁定按鈕
                        const response = await fetch(`/winners_fragment/${giftId}`);
                        const html = await response.text();
                        document.getElementById('award-table').innerHTML = html;
                        const reassignButtons = document.querySelectorAll('.reassign-btn');
                        bindRedrawEvent(reassignButtons);

                    } else {
                        throw new Error('重抽失敗');
                    }
                })
                .then(response => response.text())
                .then(newHtml => {
                    // 更新得獎者清單
                    document.getElementById('award-table').innerHTML = newHtml;
                    // 再次綁定事件，確保新內容的按鈕可用
                    // （如果有需要，可以遞迴調用或封裝成函數）
                })
                .catch(error => console.error('Error:', error));
        });
    });
}
