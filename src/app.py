from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    @app.route('/index')
    def index():
        return render_template(
            'index.html', title='home'
        )
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)