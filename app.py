from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from pytube import YouTube, Playlist

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    link = request.form['link']
    stream_resolution = int(request.form['resolution'])

    try:
        if 'playlist' in link.lower():
            # Handle Playlist URL
            ytp = Playlist(link)
            for video in ytp.videos:
                try:
                    download_single_video(video.watch_url, stream_resolution)
                except Exception as e:
                    message = f"Error downloading video: {str(e)}"
        else:
            # Handle Single Video URL
            download_single_video(link, stream_resolution)
        
        message = "Download(s) completed successfully"
    except Exception as e:
        message = f"Error: {str(e)}"

    return render_template('index.html', message=message)

def download_single_video(video_url, resolution):
    yt = YouTube(video_url)
    title = yt.title
    streams = yt.streams.filter(progressive=True).order_by('resolution').desc()

    if 0 <= resolution < len(streams):
        selected_stream = streams[resolution]

        # Emit initial progress
        emit('update_progress', {'progress': 10}, namespace='/test', broadcast=True)

        selected_stream.download()

        # Emit completion progress
        emit('update_progress', {'progress': 100}, namespace='/test', broadcast=True)

        print(f"Successfully Downloaded Video: {title}")
    else:
        print("Invalid stream selection. Aborting.")

if __name__ == '__main__':
    socketio.run(app, debug=True)
