"""
Media Extractor - Extract images, videos, and audio with comprehensive metadata
"""
import logging
from typing import Dict, List, Any, Optional, Set
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)


class MediaExtractor:
    """
    Extract media content from HTML with comprehensive metadata
    
    Supports:
    - Images (img, picture, srcset)
    - Videos (video, iframe embeds)
    - Audio (audio)
    - Metadata extraction (alt text, dimensions, captions, sources)
    """
    
    def __init__(self):
        """Initialize media extractor"""
        self.video_domains = {
            'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com',
            'wistia.com', 'vidyard.com', 'brightcove.com'
        }
    
    def extract(self, soup: BeautifulSoup, base_url: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract all media from HTML
        
        Args:
            soup: BeautifulSoup parsed HTML
            base_url: Base URL for resolving relative URLs
            
        Returns:
            Dictionary containing:
                - images: List of image data
                - videos: List of video data
                - audio: List of audio data
                - embeds: List of embedded media
        """
        return {
            'images': self.extract_images(soup, base_url),
            'videos': self.extract_videos(soup, base_url),
            'audio': self.extract_audio(soup, base_url),
            'embeds': self.extract_embeds(soup, base_url)
        }
    
    def extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """
        Extract images with comprehensive metadata
        
        Extracts:
        - Regular img tags
        - Picture elements with source sets
        - Responsive images (srcset)
        - Figure captions
        - Schema.org ImageObject data
        """
        images = []
        seen_urls: Set[str] = set()
        
        # Extract regular img tags
        for img in soup.find_all('img'):
            image_data = self._extract_image_data(img, base_url)
            
            if image_data and image_data['src'] not in seen_urls:
                seen_urls.add(image_data['src'])
                images.append(image_data)
        
        # Extract picture elements
        for picture in soup.find_all('picture'):
            image_data = self._extract_picture_data(picture, base_url)
            
            if image_data and image_data['src'] not in seen_urls:
                seen_urls.add(image_data['src'])
                images.append(image_data)
        
        return images
    
    def _extract_image_data(self, img: Tag, base_url: str) -> Optional[Dict[str, Any]]:
        """Extract data from img tag"""
        src = img.get('src', '').strip()
        
        if not src:
            # Try data-src (lazy loading)
            src = img.get('data-src', '').strip()
        
        if not src:
            return None
        
        # Make absolute URL
        absolute_url = urljoin(base_url, src)
        
        image_data = {
            'src': absolute_url,
            'alt': img.get('alt', ''),
            'title': img.get('title', ''),
            'width': img.get('width', ''),
            'height': img.get('height', ''),
            'loading': img.get('loading', ''),
            'decoding': img.get('decoding', ''),
            'sizes': img.get('sizes', ''),
            'type': 'img'
        }
        
        # Extract srcset
        srcset = img.get('srcset', '')
        if srcset:
            image_data['srcset'] = self._parse_srcset(srcset, base_url)
        
        # Check if it's in a figure with caption
        figure = img.find_parent('figure')
        if figure:
            caption = figure.find('figcaption')
            if caption:
                image_data['caption'] = caption.get_text(strip=True)
        
        # Check for data attributes (custom metadata)
        data_attrs = {}
        for attr, value in img.attrs.items():
            if attr.startswith('data-'):
                data_attrs[attr] = value
        
        if data_attrs:
            image_data['data_attributes'] = data_attrs
        
        # Check for schema.org ImageObject
        if img.get('itemprop') == 'image':
            image_data['schema_type'] = 'ImageObject'
        
        return image_data
    
    def _extract_picture_data(self, picture: Tag, base_url: str) -> Optional[Dict[str, Any]]:
        """Extract data from picture element"""
        # Get the fallback img tag
        img = picture.find('img')
        if not img:
            return None
        
        image_data = self._extract_image_data(img, base_url)
        if not image_data:
            return None
        
        image_data['type'] = 'picture'
        
        # Extract source elements
        sources = []
        for source in picture.find_all('source'):
            source_data = {
                'srcset': source.get('srcset', ''),
                'media': source.get('media', ''),
                'type': source.get('type', ''),
                'sizes': source.get('sizes', '')
            }
            
            if source_data['srcset']:
                source_data['srcset_parsed'] = self._parse_srcset(source_data['srcset'], base_url)
            
            sources.append(source_data)
        
        if sources:
            image_data['sources'] = sources
        
        return image_data
    
    def _parse_srcset(self, srcset: str, base_url: str) -> List[Dict[str, str]]:
        """Parse srcset attribute into structured data"""
        parsed_srcset = []
        
        # Split by comma, handle multiple entries
        entries = srcset.split(',')
        
        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue
            
            # Split by space to separate URL from descriptor
            parts = entry.split()
            if not parts:
                continue
            
            url = parts[0]
            descriptor = parts[1] if len(parts) > 1 else '1x'
            
            parsed_srcset.append({
                'url': urljoin(base_url, url),
                'descriptor': descriptor
            })
        
        return parsed_srcset
    
    def extract_videos(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """
        Extract video elements with metadata
        
        Extracts:
        - HTML5 video tags
        - Video sources
        - Poster images
        - Track elements (captions, subtitles)
        """
        videos = []
        
        for video in soup.find_all('video'):
            video_data = {
                'type': 'video',
                'poster': video.get('poster', ''),
                'width': video.get('width', ''),
                'height': video.get('height', ''),
                'controls': video.has_attr('controls'),
                'autoplay': video.has_attr('autoplay'),
                'loop': video.has_attr('loop'),
                'muted': video.has_attr('muted'),
                'preload': video.get('preload', 'auto')
            }
            
            # Make poster URL absolute
            if video_data['poster']:
                video_data['poster'] = urljoin(base_url, video_data['poster'])
            
            # Extract sources
            sources = []
            for source in video.find_all('source'):
                src = source.get('src', '')
                if src:
                    sources.append({
                        'src': urljoin(base_url, src),
                        'type': source.get('type', ''),
                        'quality': source.get('data-quality', '')
                    })
            
            # If no sources, check for src attribute on video tag
            if not sources and video.get('src'):
                sources.append({
                    'src': urljoin(base_url, video.get('src')),
                    'type': video.get('type', '')
                })
            
            video_data['sources'] = sources
            
            # Extract tracks (captions, subtitles)
            tracks = []
            for track in video.find_all('track'):
                tracks.append({
                    'src': urljoin(base_url, track.get('src', '')),
                    'kind': track.get('kind', 'subtitles'),
                    'srclang': track.get('srclang', ''),
                    'label': track.get('label', '')
                })
            
            if tracks:
                video_data['tracks'] = tracks
            
            videos.append(video_data)
        
        return videos
    
    def extract_audio(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract audio elements with metadata"""
        audio_list = []
        
        for audio in soup.find_all('audio'):
            audio_data = {
                'type': 'audio',
                'controls': audio.has_attr('controls'),
                'autoplay': audio.has_attr('autoplay'),
                'loop': audio.has_attr('loop'),
                'muted': audio.has_attr('muted'),
                'preload': audio.get('preload', 'auto')
            }
            
            # Extract sources
            sources = []
            for source in audio.find_all('source'):
                src = source.get('src', '')
                if src:
                    sources.append({
                        'src': urljoin(base_url, src),
                        'type': source.get('type', '')
                    })
            
            # If no sources, check for src attribute
            if not sources and audio.get('src'):
                sources.append({
                    'src': urljoin(base_url, audio.get('src')),
                    'type': audio.get('type', '')
                })
            
            audio_data['sources'] = sources
            
            audio_list.append(audio_data)
        
        return audio_list
    
    def extract_embeds(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """
        Extract embedded media (YouTube, Vimeo, etc.)
        
        Extracts:
        - iframe embeds
        - Embed tags
        - Object tags
        """
        embeds = []
        
        # Extract iframes
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '').strip()
            if not src:
                continue
            
            embed_data = {
                'type': 'iframe',
                'src': urljoin(base_url, src),
                'width': iframe.get('width', ''),
                'height': iframe.get('height', ''),
                'title': iframe.get('title', ''),
                'allow': iframe.get('allow', ''),
                'sandbox': iframe.get('sandbox', '')
            }
            
            # Identify embed type
            parsed_url = urlparse(embed_data['src'])
            domain = parsed_url.netloc.replace('www.', '')
            
            if any(vid_domain in domain for vid_domain in self.video_domains):
                embed_data['embed_type'] = 'video'
                embed_data['platform'] = self._identify_video_platform(domain)
                
                # Extract video ID for YouTube/Vimeo
                if 'youtube.com' in domain or 'youtu.be' in domain:
                    video_id = self._extract_youtube_id(embed_data['src'])
                    if video_id:
                        embed_data['video_id'] = video_id
                
                elif 'vimeo.com' in domain:
                    video_id = self._extract_vimeo_id(embed_data['src'])
                    if video_id:
                        embed_data['video_id'] = video_id
            
            embeds.append(embed_data)
        
        # Extract embed tags
        for embed in soup.find_all('embed'):
            src = embed.get('src', '').strip()
            if src:
                embeds.append({
                    'type': 'embed',
                    'src': urljoin(base_url, src),
                    'width': embed.get('width', ''),
                    'height': embed.get('height', ''),
                    'media_type': embed.get('type', '')
                })
        
        return embeds
    
    def _identify_video_platform(self, domain: str) -> str:
        """Identify video platform from domain"""
        if 'youtube' in domain:
            return 'YouTube'
        elif 'vimeo' in domain:
            return 'Vimeo'
        elif 'dailymotion' in domain:
            return 'Dailymotion'
        elif 'wistia' in domain:
            return 'Wistia'
        elif 'vidyard' in domain:
            return 'Vidyard'
        elif 'brightcove' in domain:
            return 'Brightcove'
        
        return 'Unknown'
    
    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_vimeo_id(self, url: str) -> Optional[str]:
        """Extract Vimeo video ID from URL"""
        pattern = r'vimeo\.com\/(?:video\/)?(\d+)'
        match = re.search(pattern, url)
        
        if match:
            return match.group(1)
        
        return None
