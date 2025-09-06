/**
 * LLM.txt Generator - Frontend Application
 * =======================================
 * Professional JavaScript application with real-time updates,
 * smooth animations, and comprehensive error handling.
 */

class LLMGeneratorApp {
    constructor() {
        this.socket = null;
        this.currentJobId = null;
        this.currentResults = [];
        this.isProcessing = false;
        
        this.init();
    }
    
    init() {
        console.log('Initializing LLM.txt Generator App...');
        this.initializeSocketIO();
        this.bindEvents();
        this.initializeAnimations();
        
        console.log('🚀 LLM.txt Generator App initialized');
    }
    
    initializeSocketIO() {
        // Check if SocketIO is available
        if (typeof io === 'undefined') {
            console.warn('SocketIO library not loaded! Running in offline mode.');
            this.socket = null;
            return;
        }
        
        console.log('Initializing SocketIO connection...');
        // Initialize Socket.IO connection
        this.socket = io();
        
        // Socket event handlers
        this.socket.on('connect', () => {
            console.log('🔌 Connected to server');
            this.showNotification('Connected to server', 'success');
        });
        
        this.socket.on('disconnect', () => {
            console.log('🔌 Disconnected from server');
            this.showNotification('Disconnected from server', 'warning');
        });
        
        this.socket.on('job_log', (data) => {
            this.handleJobLog(data);
        });
        
        this.socket.on('job_status', (data) => {
            this.handleJobStatus(data);
        });
        
        this.socket.on('job_error', (data) => {
            this.handleJobError(data);
        });
        
        this.socket.on('job_complete', (data) => {
            this.handleJobComplete(data);
        });
    }
    
    bindEvents() {
        // URL form submission
        const urlForm = document.getElementById('urlForm');
        if (urlForm) {
            console.log('Binding form submit event');
            urlForm.addEventListener('submit', (e) => {
                console.log('Form submit event fired');
                this.handleFormSubmit(e);
            });
        } else {
            console.error('URL form not found!');
        }
        
        // Also bind to the submit button directly as backup
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            console.log('Binding submit button click event');
            submitBtn.addEventListener('click', (e) => {
                console.log('Submit button clicked');
                e.preventDefault();
                // Trigger the form submit instead of duplicating logic
                const form = document.getElementById('urlForm');
                if (form) {
                    console.log('Dispatching form submit event');
                    form.dispatchEvent(new Event('submit'));
                } else {
                    console.error('Form not found when button clicked');
                }
            });
        } else {
            console.error('Submit button not found!');
        }
        
        // Button events
        this.bindButton('exportBtn', () => this.exportResults());
        this.bindButton('newAnalysisBtn', () => this.startNewAnalysis());
        this.bindButton('retryBtn', () => this.retryAnalysis());
        this.bindButton('backToHomeBtn', () => this.goToHome());
        this.bindButton('logsToggle', () => this.toggleLogs());
        this.bindButton('modalClose', () => this.closeModal());
        this.bindButton('copyContentBtn', () => this.copyModalContent());
        this.bindButton('downloadContentBtn', () => this.downloadModalContent());
        
        // Search input
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.filterResults(e.target.value));
        }
        
        // Modal background click to close
        const modal = document.getElementById('contentModal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }
    
    bindButton(id, handler) {
        const button = document.getElementById(id);
        if (button) {
            button.addEventListener('click', handler);
        }
    }
    
    initializeAnimations() {
        // Add entrance animations to elements
        const animatedElements = document.querySelectorAll('.feature-card');
        animatedElements.forEach((el, index) => {
            el.style.animationDelay = `${index * 0.1}s`;
            el.classList.add('animate-fade-in');
        });
    }
    
    async handleFormSubmit(e) {
        console.log('Form submit triggered');
        e.preventDefault();
        
        if (this.isProcessing) {
            this.showNotification('Analysis already in progress', 'warning');
            return;
        }
        
        const urlInput = document.getElementById('websiteUrl');
        const url = urlInput.value.trim();
        
        console.log('URL input value:', url);
        
        if (!url) {
            console.log('URL is empty');
            this.showNotification('Please enter a valid URL', 'error');
            urlInput.focus();
            return;
        }
        
        // Validate URL format
        const isValid = this.isValidUrl(url);
        console.log('URL validation result:', isValid);
        
        if (!isValid) {
            console.log('URL validation failed');
            this.showNotification('Please enter a valid URL (e.g., https://example.com)', 'error');
            urlInput.focus();
            return;
        }
        
        await this.startAnalysis(url);
    }
    
    isValidUrl(string) {
        try {
            // Add protocol if missing
            const url = string.startsWith('http') ? string : `https://${string}`;
            new URL(url);
            return true;
        } catch (_) {
            return false;
        }
    }
    
    async startAnalysis(url) {
        try {
            this.isProcessing = true;
            this.showLoadingButton(true);
            
            // Make API request to start job
            const response = await fetch('/api/start-job', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to start analysis');
            }
            
            this.currentJobId = data.job_id;
            
            // Join the job room for real-time updates (if socket is available)
            if (this.socket) {
                this.socket.emit('join_job', { job_id: this.currentJobId });
            }
            
            // Switch to processing view
            this.showProcessingSection(url);
            
            // Initialize progress tracking
            this.initializeProgress();
            
            // Start polling for updates if no socket connection
            if (!this.socket) {
                this.startPolling();
            }
            
            this.showNotification('Analysis started successfully!', 'success');
            
        } catch (error) {
            console.error('Error starting analysis:', error);
            this.showError(error.message);
            this.isProcessing = false;
            this.showLoadingButton(false);
        }
    }
    
    showProcessingSection(url) {
        // Hide hero section
        const heroSection = document.getElementById('heroSection');
        if (heroSection) {
            heroSection.style.display = 'none';
        }
        
        // Show processing section
        const processingSection = document.getElementById('processingSection');
        if (processingSection) {
            processingSection.style.display = 'block';
            processingSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Update processing URL
        const processingUrl = document.getElementById('processingUrl');
        if (processingUrl) {
            processingUrl.textContent = url;
        }
        
        // Reset progress
        this.updateProgress(0, 'Initializing...');
        this.resetSteps();
    }
    
    initializeProgress() {
        this.updateProgress(0, 'Starting analysis...');
        this.setStepStatus(1, 'active');
    }
    
    updateProgress(percentage, status) {
        const progressFill = document.getElementById('progressFill');
        const progressPercentage = document.getElementById('progressPercentage');
        const progressStatus = document.getElementById('progressStatus');
        
        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }
        
        if (progressPercentage) {
            progressPercentage.textContent = `${percentage}%`;
        }
        
        if (progressStatus) {
            progressStatus.textContent = status;
        }
    }
    
    resetSteps() {
        for (let i = 1; i <= 4; i++) {
            this.setStepStatus(i, 'waiting');
        }
    }
    
    setStepStatus(stepNumber, status) {
        const step = document.getElementById(`step${stepNumber}`);
        if (!step) return;
        
        // Remove all status classes
        step.classList.remove('active', 'completed', 'error');
        
        // Add new status class
        if (status !== 'waiting') {
            step.classList.add(status);
        }
        
        // Update step status icon
        const statusIcon = step.querySelector('.step-status i');
        if (statusIcon) {
            statusIcon.className = this.getStatusIconClass(status);
        }
    }
    
    getStatusIconClass(status) {
        switch (status) {
            case 'waiting':
                return 'fas fa-clock waiting';
            case 'active':
                return 'fas fa-spinner fa-spin processing';
            case 'completed':
                return 'fas fa-check completed';
            case 'error':
                return 'fas fa-times error';
            default:
                return 'fas fa-clock waiting';
        }
    }
    
    handleJobLog(data) {
        if (data.job_id !== this.currentJobId) return;
        
        this.addLogEntry(data.log);
    }
    
    handleJobStatus(data) {
        if (data.job_id !== this.currentJobId) return;
        
        this.updateProgress(data.progress, data.status);
        this.updateStepsBasedOnStatus(data.status, data.progress);
        
        // Ensure logs stay scrolled to bottom on status updates
        this.forceScrollToBottom();
    }
    
    handleJobError(data) {
        if (data.job_id !== this.currentJobId) return;
        
        this.showError(data.error);
        this.isProcessing = false;
        
        // Ensure logs stay scrolled to bottom on errors
        this.forceScrollToBottom();
    }
    
    handleJobComplete(data) {
        if (data.job_id !== this.currentJobId) return;
        
        this.currentResults = data.results;
        this.showResults();
        this.isProcessing = false;
    }
    
    updateStepsBasedOnStatus(status, progress) {
        // Update steps based on status and progress for step-by-step approach
        if (status === 'generating_sitemap' || progress < 15) {
            this.setStepStatus(1, 'active');
            this.setStepStatus(2, 'pending');
            this.setStepStatus(3, 'pending');
            this.setStepStatus(4, 'pending');
        } else if (status === 'extracting_urls' || (progress >= 15 && progress < 25)) {
            this.setStepStatus(1, 'completed');
            this.setStepStatus(2, 'active');
            this.setStepStatus(3, 'pending');
            this.setStepStatus(4, 'pending');
        } else if (status === 'scraping_text' || (progress >= 25 && progress < 50)) {
            this.setStepStatus(1, 'completed');
            this.setStepStatus(2, 'completed');
            this.setStepStatus(3, 'active');
            this.setStepStatus(4, 'pending');
        } else if (status === 'taking_screenshots' || (progress >= 50 && progress < 75)) {
            this.setStepStatus(1, 'completed');
            this.setStepStatus(2, 'completed');
            this.setStepStatus(3, 'completed');
            this.setStepStatus(4, 'active');
        } else if (status === 'generating_llm' || (progress >= 75 && progress < 95)) {
            this.setStepStatus(1, 'completed');
            this.setStepStatus(2, 'completed');
            this.setStepStatus(3, 'completed');
            this.setStepStatus(4, 'active');
        } else if (status === 'finalizing' || (progress >= 95 && progress < 100)) {
            this.setStepStatus(1, 'completed');
            this.setStepStatus(2, 'completed');
            this.setStepStatus(3, 'completed');
            this.setStepStatus(4, 'active');
        } else if (status === 'completed') {
            for (let i = 1; i <= 4; i++) {
                this.setStepStatus(i, 'completed');
            }
        }
        
        // Update step titles based on current status
        this.updateStepTitles(status);
    }
    
    updateStepTitles(status) {
        const step1 = document.querySelector('#step1 .step-content h3');
        const step2 = document.querySelector('#step2 .step-content h3');
        const step3 = document.querySelector('#step3 .step-content h3');
        const step4 = document.querySelector('#step4 .step-content h3');
        
        if (status === 'generating_sitemap') {
            if (step1) step1.textContent = 'Generating Sitemap';
        } else if (status === 'extracting_urls') {
            if (step2) step2.textContent = 'Extracting URLs';
        } else if (status === 'scraping_text') {
            if (step3) step3.textContent = 'Scraping Text Content';
        } else if (status === 'taking_screenshots') {
            if (step4) step4.textContent = 'Taking Screenshots';
        } else if (status === 'generating_llm') {
            if (step4) step4.textContent = 'Generating LLM.txt';
        }
    }
    
    addLogEntry(log) {
        const logsContent = document.getElementById('logsContent');
        if (!logsContent) return;
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${log.level}`;
        logEntry.innerHTML = `
            <span class="log-timestamp">${log.timestamp}</span>
            <span class="log-message">${this.escapeHtml(log.message)}</span>
        `;
        
        logsContent.appendChild(logEntry);
        
        // Force scroll to bottom with multiple methods for reliability
        this.forceScrollToBottom();
    }
    
    forceScrollToBottom() {
        const logsContent = document.getElementById('logsContent');
        if (!logsContent) return;
        
        // Immediate scroll
        logsContent.scrollTop = logsContent.scrollHeight;
        
        // Multiple attempts with different timings
        setTimeout(() => {
            logsContent.scrollTop = logsContent.scrollHeight;
        }, 10);
        
        setTimeout(() => {
            logsContent.scrollTop = logsContent.scrollHeight;
        }, 50);
        
        setTimeout(() => {
            logsContent.scrollTop = logsContent.scrollHeight;
        }, 100);
        
        // Force scroll with animation
        setTimeout(() => {
            logsContent.scrollTo({
                top: logsContent.scrollHeight,
                behavior: 'smooth'
            });
        }, 150);
    }
    
    showResults() {
        // Hide processing section
        const processingSection = document.getElementById('processingSection');
        if (processingSection) {
            processingSection.style.display = 'none';
        }
        
        // Show results section
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Update results summary
        const resultsSummary = document.getElementById('resultsSummary');
        if (resultsSummary) {
            resultsSummary.textContent = `Successfully generated LLM.txt files for ${this.currentResults.length} pages.`;
        }
        
        // Populate results table
        this.populateResultsTable();
        
        this.showNotification('Analysis completed successfully!', 'success');
    }
    
    populateResultsTable() {
        const tableBody = document.getElementById('resultsTableBody');
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        this.currentResults.forEach((result, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="url-cell">
                    <a href="${result.url}" target="_blank" class="url-link" title="${result.url}">
                        ${this.truncateUrl(result.url, 40)}
                    </a>
                </td>
                <td class="content-preview">
                    ${this.getContentPreview(result.llm_txt)}
                </td>
                <td class="text-count">${result.text_count || 0}</td>
                <td>
                    <span class="screenshot-status ${result.screenshot_path ? 'available' : 'unavailable'}">
                        <i class="fas ${result.screenshot_path ? 'fa-check' : 'fa-times'}"></i>
                        ${result.screenshot_path ? 'Available' : 'N/A'}
                    </span>
                </td>
                <td class="table-actions">
                    <button class="table-btn view" onclick="app.viewContent(${index})" title="View LLM.txt">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="table-btn copy" onclick="app.copyContent(${index})" title="Copy to clipboard">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button class="table-btn download" onclick="app.downloadContent(${index})" title="Download LLM.txt">
                        <i class="fas fa-download"></i>
                    </button>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
    }
    
    truncateUrl(url, maxLength) {
        if (url.length <= maxLength) return url;
        return url.substring(0, maxLength) + '...';
    }
    
    getContentPreview(content) {
        if (!content) return 'No content available';
        
        // Extract first few lines of meaningful content
        const lines = content.split('\n').filter(line => line.trim() && !line.startsWith('#'));
        const preview = lines.slice(0, 3).join(' ').substring(0, 150);
        return this.escapeHtml(preview) + (preview.length >= 150 ? '...' : '');
    }
    
    viewContent(index) {
        const result = this.currentResults[index];
        if (!result) return;
        
        const modal = document.getElementById('contentModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalContent = document.getElementById('modalContent');
        
        if (modal && modalTitle && modalContent) {
            modalTitle.textContent = `LLM.txt - ${this.truncateUrl(result.url, 50)}`;
            modalContent.textContent = result.llm_txt;
            
            modal.classList.add('show');
            modal.style.display = 'flex';
            
            // Store current content for copy/download
            this.currentModalContent = {
                url: result.url,
                content: result.llm_txt
            };
        }
    }
    
    async copyContent(index) {
        const result = this.currentResults[index];
        if (!result) return;
        
        try {
            await navigator.clipboard.writeText(result.llm_txt);
            this.showNotification('Content copied to clipboard!', 'success');
        } catch (error) {
            console.error('Failed to copy content:', error);
            this.showNotification('Failed to copy content', 'error');
        }
    }
    
    downloadContent(index) {
        const result = this.currentResults[index];
        if (!result || !result.llm_txt) {
            this.showNotification('No content available to download', 'warning');
            return;
        }
        
        // Create filename from URL
        const url = new URL(result.url);
        const filename = `${url.hostname}_${url.pathname.replace(/[^a-zA-Z0-9]/g, '_')}.txt`;
        
        // Create and download file
        const blob = new Blob([result.llm_txt], { type: 'text/plain' });
        const url_blob = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url_blob;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url_blob);
        
        this.showNotification('LLM.txt file downloaded!', 'success');
    }
    
    closeModal() {
        const modal = document.getElementById('contentModal');
        if (modal) {
            modal.classList.remove('show');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        }
    }
    
    async copyModalContent() {
        if (!this.currentModalContent) return;
        
        try {
            await navigator.clipboard.writeText(this.currentModalContent.content);
            this.showNotification('Content copied to clipboard!', 'success');
        } catch (error) {
            console.error('Failed to copy content:', error);
            this.showNotification('Failed to copy content', 'error');
        }
    }
    
    downloadModalContent() {
        if (!this.currentModalContent) return;
        
        const filename = this.getFilenameFromUrl(this.currentModalContent.url) + '_llm.txt';
        this.downloadTextFile(this.currentModalContent.content, filename);
    }
    
    getFilenameFromUrl(url) {
        try {
            const urlObj = new URL(url);
            let filename = urlObj.hostname + urlObj.pathname;
            filename = filename.replace(/[^a-zA-Z0-9]/g, '_');
            return filename || 'llm_content';
        } catch (error) {
            return 'llm_content';
        }
    }
    
    downloadTextFile(content, filename) {
        const blob = new Blob([content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        this.showNotification(`Downloaded ${filename}`, 'success');
    }
    
    async exportResults() {
        if (!this.currentJobId) return;
        
        try {
            const response = await fetch(`/api/export-results/${this.currentJobId}`);
            
            if (!response.ok) {
                throw new Error('Failed to export results');
            }
            
            // Trigger download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `llm_results_${this.currentJobId}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.showNotification('Results exported successfully!', 'success');
            
        } catch (error) {
            console.error('Export failed:', error);
            this.showNotification('Failed to export results', 'error');
        }
    }
    
    startNewAnalysis() {
        // Reset state
        this.currentJobId = null;
        this.currentResults = [];
        this.isProcessing = false;
        this.currentModalContent = null;
        
        // Hide all sections except hero
        document.getElementById('processingSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('errorSection').style.display = 'none';
        document.getElementById('heroSection').style.display = 'block';
        
        // Clear form
        const urlInput = document.getElementById('websiteUrl');
        if (urlInput) {
            urlInput.value = '';
            urlInput.focus();
        }
        
        // Reset button state
        this.showLoadingButton(false);
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    retryAnalysis() {
        this.startNewAnalysis();
    }
    
    goToHome() {
        this.startNewAnalysis();
    }
    
    toggleLogs() {
        const logsContainer = document.getElementById('logsContainer');
        const toggleIcon = document.querySelector('#logsToggle i');
        
        if (logsContainer && toggleIcon) {
            logsContainer.classList.toggle('collapsed');
            
            if (logsContainer.classList.contains('collapsed')) {
                toggleIcon.className = 'fas fa-chevron-right';
            } else {
                toggleIcon.className = 'fas fa-chevron-down';
            }
        }
    }
    
    filterResults(searchTerm) {
        const tableBody = document.getElementById('resultsTableBody');
        if (!tableBody) return;
        
        const rows = tableBody.querySelectorAll('tr');
        const term = searchTerm.toLowerCase();
        
        rows.forEach(row => {
            const url = row.querySelector('.url-link').textContent.toLowerCase();
            const content = row.querySelector('.content-preview').textContent.toLowerCase();
            
            if (url.includes(term) || content.includes(term)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    showError(message) {
        // Hide other sections
        document.getElementById('heroSection').style.display = 'none';
        document.getElementById('processingSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'none';
        
        // Show error section
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');
        
        if (errorSection && errorMessage) {
            errorMessage.textContent = message;
            errorSection.style.display = 'block';
            errorSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        this.showNotification(message, 'error');
        this.showLoadingButton(false);
    }
    
    showLoadingButton(loading) {
        const submitBtn = document.getElementById('submitBtn');
        if (!submitBtn) return;
        
        if (loading) {
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
        } else {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas ${this.getNotificationIcon(type)}"></i>
            <span>${this.escapeHtml(message)}</span>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1001;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            max-width: 400px;
            animation: slideInRight 0.3s ease-out;
            font-weight: 500;
        `;
        
        // Add close button functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            padding: 0.25rem;
            margin-left: auto;
        `;
        
        closeBtn.addEventListener('click', () => {
            this.removeNotification(notification);
        });
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            this.removeNotification(notification);
        }, 5000);
    }
    
    removeNotification(notification) {
        if (notification && notification.parentNode) {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }
    
    getNotificationIcon(type) {
        switch (type) {
            case 'success': return 'fa-check-circle';
            case 'error': return 'fa-exclamation-circle';
            case 'warning': return 'fa-exclamation-triangle';
            default: return 'fa-info-circle';
        }
    }
    
    getNotificationColor(type) {
        switch (type) {
            case 'success': return '#48bb78';
            case 'error': return '#f56565';
            case 'warning': return '#ed8936';
            default: return '#667eea';
        }
    }
    
    handleKeyboard(e) {
        // ESC to close modal
        if (e.key === 'Escape') {
            this.closeModal();
        }
        
        // Ctrl+Enter to start analysis (when focused on URL input)
        if (e.ctrlKey && e.key === 'Enter') {
            const urlInput = document.getElementById('websiteUrl');
            if (document.activeElement === urlInput) {
                const form = document.getElementById('urlForm');
                if (form) {
                    form.dispatchEvent(new Event('submit'));
                }
            }
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    async startPolling() {
        // Start polling for job updates when SocketIO is not available
        if (!this.currentJobId) return;
        
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/job-status/${this.currentJobId}`);
                const data = await response.json();
                
                if (data.status === 'completed') {
                    clearInterval(pollInterval);
                    this.currentResults = data.results;
                    this.showResults();
                    this.isProcessing = false;
                } else if (data.status === 'error') {
                    clearInterval(pollInterval);
                    this.showError(data.error);
                    this.isProcessing = false;
                } else {
                    // Update progress
                    this.updateProgress(data.progress, data.status);
                    this.updateStepsBasedOnStatus(data.status, data.progress);
                    
                    // Add logs
                    if (data.logs && data.logs.length > 0) {
                        const latestLogs = data.logs.slice(-5); // Show last 5 logs
                        latestLogs.forEach(log => this.addLogEntry(log));
                        // Force scroll after adding logs
                        this.forceScrollToBottom();
                    }
                }
            } catch (error) {
                console.error('Polling error:', error);
            }
        }, 2000); // Poll every 2 seconds
        
        // Store interval ID for cleanup
        this.pollInterval = pollInterval;
    }
}

// CSS for notifications animation
const notificationStyles = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
`;

// Add notification styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// Initialize the application when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing app...');
    try {
        app = new LLMGeneratorApp();
        // Make app globally available for onclick handlers
        window.app = app;
        console.log('App initialized and available globally');
    } catch (error) {
        console.error('Failed to initialize app:', error);
        // Show error to user
        alert('Failed to initialize the application. Please check the console for details.');
    }
});

// Global error handler
window.addEventListener('error', (e) => {
    console.error('Global JavaScript error:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
});
