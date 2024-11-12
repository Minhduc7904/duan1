document.addEventListener("DOMContentLoaded", function () {
    const openMenuBtn = document.getElementById("openMenu");
    const closeMenuBtn = document.getElementById("closeMenu");
    const sideMenu = document.getElementById("sideMenu");
    const submitAnswersBtn = document.getElementById("submitAnswers");

    // Mở menu
    openMenuBtn.addEventListener("click", () => {
        sideMenu.classList.add("open");
    });

    // Đóng menu
    closeMenuBtn.addEventListener("click", () => {
        sideMenu.classList.remove("open");
    });

    // Nộp đáp án
    submitAnswersBtn.addEventListener("click", () => {
        const answers = {};

        // Thu thập đáp án trắc nghiệm
        for (let i = 1; i <= 12; i++) {
            const selectedOption = document.querySelector(`input[name="question-${i}"]:checked`);
            answers[`question-${i}`] = selectedOption ? selectedOption.value : null;
        }

        // Thu thập đáp án đúng/sai
        for (let i = 1; i <= 4; i++) {
            ['a', 'b', 'c', 'd'].forEach((suffix) => {
                const selectedOption = document.querySelector(`input[name="tf-question-${i}-${suffix}"]:checked`);
                answers[`tf-question-${i}-${suffix}`] = selectedOption ? selectedOption.value : null;
            });
        }

        // Thu thập đáp án trả lời ngắn
        for (let i = 1; i <= 6; i++) {
            const shortAnswer = document.querySelector(`#short-answer-${i}`);
            answers[`short-answer-${i}`] = shortAnswer ? shortAnswer.value : '';
        }

        // Gửi dữ liệu đến server
        fetch('/submit_answers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(answers),
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            console.error('Lỗi:', error);
        });
    });
});
