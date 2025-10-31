// Quiz JavaScript

let currentQuestion = 1;
const totalQuestions = 8;
let quizData = {};

function startQuiz() {
    document.getElementById('quiz-intro').style.display = 'none';
    document.getElementById('quiz-container').style.display = 'block';
    updateProgress();
}

function nextQuestion() {
    // Get current question
    const currentQuestionEl = document.querySelector(`.question[data-question="${currentQuestion}"]`);
    
    // Validate current question
    const inputs = currentQuestionEl.querySelectorAll('input[type="radio"]');
    let answered = false;
    
    inputs.forEach(input => {
        if (input.checked) {
            answered = true;
            quizData[input.name] = input.value;
        }
    });
    
    if (!answered) {
        alert('Please select an option before continuing.');
        return;
    }
    
    // Move to next question
    if (currentQuestion < totalQuestions) {
        currentQuestionEl.classList.remove('active');
        currentQuestion++;
        document.querySelector(`.question[data-question="${currentQuestion}"]`).classList.add('active');
        updateProgress();
        updateButtons();
    }
}

function previousQuestion() {
    if (currentQuestion > 1) {
        document.querySelector(`.question[data-question="${currentQuestion}"]`).classList.remove('active');
        currentQuestion--;
        document.querySelector(`.question[data-question="${currentQuestion}"]`).classList.add('active');
        updateProgress();
        updateButtons();
    }
}

function updateProgress() {
    const progress = (currentQuestion / totalQuestions) * 100;
    document.getElementById('progress-fill').style.width = progress + '%';
    document.getElementById('progress-text').textContent = `Question ${currentQuestion} of ${totalQuestions}`;
}

function updateButtons() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');
    
    // Show/hide previous button
    if (currentQuestion === 1) {
        prevBtn.style.display = 'none';
    } else {
        prevBtn.style.display = 'inline-block';
    }
    
    // Show/hide next vs submit button
    if (currentQuestion === totalQuestions) {
        nextBtn.style.display = 'none';
        submitBtn.style.display = 'inline-block';
    } else {
        nextBtn.style.display = 'inline-block';
        submitBtn.style.display = 'none';
    }
}

// Handle form submission
document.getElementById('quiz-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // First, collect the final question's answer (sleep_associations)
    const finalQuestionEl = document.querySelector(`.question[data-question="${totalQuestions}"]`);
    const finalInputs = finalQuestionEl.querySelectorAll('input[type="radio"]');
    let finalAnswered = false;
    
    finalInputs.forEach(input => {
        if (input.checked) {
            finalAnswered = true;
            quizData[input.name] = input.value;
        }
    });
    
    if (!finalAnswered) {
        alert('Please select an option for the final question before continuing.');
        return;
    }
    
    // Get email and name
    const email = document.getElementById('email').value;
    const name = document.getElementById('name').value;
    
    if (!email) {
        alert('Please enter your email address.');
        return;
    }
    
    // Add email and name to quiz data
    quizData.email = email;
    quizData.name = name;
    
    // Show loading state
    document.getElementById('quiz-container').style.display = 'none';
    document.getElementById('loading-state').style.display = 'block';
    
    try {
        // Submit quiz to backend
        const response = await fetch('/api/quiz/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(quizData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Create Stripe checkout session
            const checkoutResponse = await fetch('/api/payment/create-checkout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    customer_id: data.customer_id,
                    quiz_id: data.quiz_id
                })
            });
            
            const checkoutData = await checkoutResponse.json();
            
            if (checkoutData.success) {
                // Redirect to Stripe Checkout
                window.location.href = checkoutData.checkout_url;
            } else {
                throw new Error('Failed to create checkout session');
            }
        } else {
            throw new Error('Failed to submit quiz');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Something went wrong. Please try again or contact support@napocalypse.com');
        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('quiz-container').style.display = 'block';
    }
});

// Handle radio button selection styling
document.querySelectorAll('.option').forEach(option => {
    option.addEventListener('click', function() {
        const radio = this.querySelector('input[type="radio"]');
        radio.checked = true;
        
        // Remove selected class from siblings
        this.parentElement.querySelectorAll('.option').forEach(opt => {
            opt.style.borderColor = '#ecf0f1';
            opt.style.background = '#f8f9fa';
        });
        
        // Add selected styling
        this.style.borderColor = '#3498db';
        this.style.background = '#e8f4f8';
    });
});