import yt_dlp
import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.prompt import Prompt
from rich.panel import Panel
from rich import print as rprint
import re
import requests

console = Console()

def sanitize_filename(title):
    # Remove invalid characters and limit length
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    return title[:100]

def get_video_info(url):
    """Get video information"""
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:
            console.print("[red]Error getting video info: " + str(e) + "[/red]")
            return None

def download_video(url, quality='best', audio_only=False):
    """Download video with progress bar"""
    output_template = "%(title)s.%(ext)s"
    
    if audio_only:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
        }
    else:
        ydl_opts = {
            'format': quality,
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
        }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("[cyan]Downloading...", total=None)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url)
                progress.update(task, completed=100)
                return True, info.get('title', 'video')
        except Exception as e:
            console.print("[red]Error: " + str(e) + "[/red]")
            return False, str(e)

def download_file(url):
    """Download file from URL with progress bar"""
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
        )
        task = progress.add_task(f"[cyan]Downloading {local_filename}...", total=total_size)
        
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                progress.update(task, advance=len(chunk))
        progress.update(task, completed=total_size)
    console.print(f"[green]✓ Successfully downloaded: {local_filename}[/green]")
    return local_filename

def format_size(bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} TB"

def main():
    try:
        console.clear()
        console.print(Panel.fit(
            "[cyan]YouTube Downloader[/cyan]\n[yellow]Ahmed Frieg[/yellow]\n[yellow]All rights reserved to Ahmed Mohamed Frieg - Computer Geek[/yellow]",
            border_style="blue"
        ))

        while True:
            url = Prompt.ask("\n[cyan]Enter YouTube URL or file URL[/cyan]")
            if not url:
                break

            if url.startswith("http"):
                if "youtube.com" in url or "youtu.be" in url:
                    info = get_video_info(url)
                    if not info:
                        continue

                    console.print("\n[green]Title:[/green] " + info['title'])
                    console.print("[green]Duration:[/green] " + info.get('duration_string', 'N/A'))
                    console.print("[green]Channel:[/green] " + info.get('uploader', 'N/A'))

                    console.print("\n[yellow]Available Options:[/yellow]")
                    console.print("[yellow]1:[/yellow] Video (1080HD)")
                    console.print("[yellow]2:[/yellow] Video (720p)")
                    console.print("[yellow]3:[/yellow] Audio Only (MP3)")

                    download_type = Prompt.ask(
                        "\n[cyan]Enter your choice[/cyan]",
                        choices=["1", "2", "3"],
                        default="1"
                    )

                    if download_type == "1":
                        success, result = download_video(url, 'best[height<=1080]')
                    elif download_type == "2":
                        success, result = download_video(url, 'best[height<=720]')
                    else:
                        success, result = download_video(url, audio_only=True)

                    if success:
                        console.print("\n[green]✓ Successfully downloaded: " + result + "[/green]")
                    else:
                        console.print("\n[red]✗ Download failed: " + result + "[/red]")

                else:
                    download_file(url)

            if not Prompt.ask("\n[cyan]Download another video or file?[/cyan]", choices=["y", "n"], default="y") == "y":
                break

        console.print("\n[cyan]Thanks for using YouTube Downloader! Goodbye egyptions![/cyan]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Download cancelled by user[/yellow]")
    except Exception as e:
        console.print("\n[red]An unexpected error occurred: " + str(e) + "[/red]")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
