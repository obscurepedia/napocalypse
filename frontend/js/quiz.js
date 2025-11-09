// Quiz JavaScript

let currentQuestion = 1;
const totalQuestions = 8;
let quizData = {};

function startQuiz() {
    document.getElementById('quiz-intro').style.display = 'none';
    document.getElementById('quiz-container').style.display = 'block';
    showQuestion(1);
    updateProgress();
}

function selectOption(questionNum, value) {
    // Store the answer
    quizData[`question${questionNum}`] = value;
    
    // Show next question or finish quiz
    if (questionNum < totalQuestions) {
        showQuestion(questionNum + 1);
        currentQuestion = questionNum + 1;
        updateProgress();
    } else {
        // For question 8, scroll to the email form after selection
        finishQuiz();
        setTimeout(() => {
            const emailContainer = document.querySelector('.email-input-container');
            const scrollIndicator = document.querySelector('.scroll-indicator');
            
            if (emailContainer) {
                // Add highlighting effect
                emailContainer.classList.add('highlighted');
                
                // Show the scroll indicator
                if (scrollIndicator) {
                    scrollIndicator.style.opacity = '1';
                }
                
                // Scroll to the email form
                emailContainer.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' 
                });
                
                // Focus on the email input to draw attention
                setTimeout(() => {
                    const emailInput = document.getElementById('email');
                    if (emailInput) {
                        emailInput.focus();
                    }
                }, 500);
            }
        }, 300); // Small delay to ensure smooth scrolling
    }
}

function showQuestion(questionNum) {
    // Hide all questions
    const allQuestions = document.querySelectorAll('.question');
    allQuestions.forEach(q => q.style.display = 'none');
    
    // Show current question
    const currentQ = document.getElementById(`question-${questionNum}`);
    if (currentQ) {
        currentQ.style.display = 'block';
    }
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
    
    // Check if we have answered question 8 (sleep associations)
    if (!quizData.question8) {
        alert('Please select how your baby currently falls asleep before continuing.');
        return;
    }
    
    // Get email and name
    const email = document.getElementById('email').value;
    const name = document.getElementById('name').value;
    
    if (!email) {
        alert('Please enter your email address.');
        return;
    }
    
    // Map question data to expected field names
    const submissionData = {
        email: email,
        name: name || '',
        baby_age: quizData.question1,
        sleep_situation: quizData.question2,
        sleep_philosophy: quizData.question3,
        living_situation: quizData.question4,
        parenting_setup: quizData.question5,
        work_schedule: quizData.question6,
        biggest_challenge: quizData.question7,
        sleep_associations: quizData.question8
    };
    
    console.log('Quiz data being sent:', submissionData);
    console.log('Original quiz data:', quizData);
    
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
            body: JSON.stringify(submissionData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${data.error || 'Unknown error'}`);
        }
        
        if (data.success) {
            console.log('Quiz submitted successfully:', data);
            
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
                throw new Error(`Failed to create checkout session: ${checkoutData.error || 'Unknown error'}`);
            }
        } else {
            throw new Error('Failed to submit quiz');
        }
    } catch (error) {
        console.error('Error:', error);
        
        // Try to get more specific error information
        if (error.response) {
            console.error('Response data:', error.response);
        }
        
        alert(`Something went wrong. Please check the console for details or contact support@napocalypse.com. Error: ${error.message}`);
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

function finishQuiz() {
    // For question 8, we need to show the email form instead of finishing
    // The email form is already part of question 8, so we don't need to do anything special
    // The form submission will be handled by the submit event listener
    console.log('Quiz completed, showing email collection for question 8');
}

function submitQuizData() {
    // This function should handle the actual quiz submission
    // For now, let's just redirect to a results page or show a message
    console.log('Quiz data:', quizData);
    alert('Quiz completed! (This would normally redirect to your personalized results)');
}