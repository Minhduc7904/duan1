document.addEventListener("DOMContentLoaded", function () {
    const mcContainer = document.getElementById("multiple-choice-questions");
    const tfContainer = document.getElementById("true-false-questions");
    const saContainer = document.getElementById("short-answer-questions");
    const answersSection = document.querySelector(".answers-section");

    // Câu hỏi trắc nghiệm
    for (let i = 1; i <= 12; i++) {
        const questionDiv = document.createElement("div");
        questionDiv.classList.add("mb-3");
        questionDiv.innerHTML = `
            <p><strong>Câu ${i}:</strong> Nội dung câu hỏi trắc nghiệm ${i}?</p>
            <ul>
                <li>A. Lựa chọn A</li>
                <li>B. Lựa chọn B</li>
                <li>C. Lựa chọn C</li>
                <li>D. Lựa chọn D</li>
            </ul>
        `;
        mcContainer.appendChild(questionDiv);
    }

    // Câu hỏi đúng sai
    for (let i = 1; i <= 4; i++) {
        const questionDiv = document.createElement("div");
        questionDiv.classList.add("mb-3");
        questionDiv.innerHTML = `
            <p><strong>Câu ${i + 12}:</strong> Nội dung câu hỏi đúng sai ${i}?</p>
            <ul>
                <li>Mệnh đề a: Nội dung mệnh đề a.</li>
                <li>Mệnh đề b: Nội dung mệnh đề b.</li>
                <li>Mệnh đề c: Nội dung mệnh đề c.</li>
                <li>Mệnh đề d: Nội dung mệnh đề d.</li>
            </ul>
        `;
        tfContainer.appendChild(questionDiv);
    }

    // Câu trả lời ngắn
    for (let i = 1; i <= 6; i++) {
        const questionDiv = document.createElement("div");
        questionDiv.classList.add("mb-3");
        questionDiv.innerHTML = `
            <p><strong>Câu ${i + 16}:</strong> Nội dung câu trả lời ngắn ${i}?</p>
            <p><em>(Câu này yêu cầu học sinh trả lời ngắn gọn.)</em></p>
        `;
        saContainer.appendChild(questionDiv);
    }
});
