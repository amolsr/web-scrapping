#include<stdio.h>
#include<conio.h>
#include<stdlib.h>
struct node
{
 int info;
 struct node *next,*previous;
};

struct node* createnode()
{
	struct node *temp;
	temp=(struct node *)malloc(sizeof(struct node));
	return(temp);
}
// INSERTING AT BEGGINING
struct node* addatbeg(struct node *START,int value)
{
	struct node *p,*q;
	p=createnode();

	p->info=value;
	p->next=NULL;
	p->previous=NULL;
	if(START==NULL)
	{
	START=p;
	p->next=START;
	p->previous=START;

	}
	else
	{
		if(START->next==START)
		{
			p->next=START;
			p->previous=START;
			START->next=p;
			START->previous=p;
			START=START->next;
		}
		else
		{
		
		p->next=START;
		p->previous=START->previous;
	    START->previous->next=p;
	   START->previous=p;
	   
	   START=p;
      }
	}
	return(START);
}

// Inserting at end
struct node* addatend(struct node *START,int val)
{
	struct node *p;
	p=createnode();
	p->info=val;
	p->next=NULL;
	p->previous=NULL;
	if(START==NULL)
	{
		START=p;
		p->next=START;
		p->previous=START;
	}
	else
	{
		if(START->next==START)
		{
		   START->next=p;
		   START->previous=p;
		   p->next=START;
		   p->previous=START;
		}
		else
		{
		
		p->previous=START->previous;
		p->next=START;
		p->previous->next=p;
		START->previous=p;
		}
	}
	return(START);
}
//SIZE OF LIST
int sizecount(struct node* START)
{
	if(START==NULL)
	{
		return(0);
	}
	else
	{
		int count=0;
	struct node *p;
	p=START;
	do
	{
		count++;
		p=p->next;
		}while(p!=START);
		return(count);	
	}
	
}
//Insert at position
struct node* addatpos(struct node *START,int pos,int value)
{
	if(START==NULL)
	{
		printf("List is empty");
	}
	else
	{
		int p;
		p=sizecount(START);
		if(pos<0 || pos>(p-1))
		printf("Invalid position !! ");
		else
		{
		         if(pos==0)
		            START=addatbeg(START,value);
		         else
		         {
		         	        
		         	        		int i;
		                         	struct node *tmp,*p;
		                         	p=createnode();
		                         	p->info=value;
		                         	p->next=NULL;
		                         	p->previous=NULL;
		                         	tmp=START;
		                         	for(i=1;i<pos;i++)
		                         	  tmp=tmp->next;
		                         	p->next=tmp->next;
		                         	p->previous=tmp;
		                         	p->next->previous=p;
		                         	tmp->next=p;
							 
				 }
			
		}
	}
	return(START);
}
//Deletion at beggining
struct node* delatbeg(struct node *START)
{
	if(START==NULL)
	    printf("List is empty");
	else
	{
		 struct node *t,*p;
		     t=START;
		     p=START;
		    if(START->next==START)
		    { 
		     START=NULL;
		     free(t);
			}
			               else
			               {
			               	while(t->next!=START)
			               	    t=t->next;
			               	t->next=START->next;
			               	START->next->previous=t;
			               	START=START->next;
			               	free(p);
						   }
	}
	return(START);
}
// Delete at end
 struct node* delatend( struct node *START)
 {
 	if(START==NULL)
 	  printf("List is empty");
 	else
 	{
 		
 		          if(START->next==START)
 		          {
 		          	struct node *t;
	                t=START;
			             START=NULL;
			             free(t);	
			       }
			       else
			       {
			       	struct node *seclast,*last;
	                last=START;
	                do
	                {
	                	seclast=last;
	                	last=last->next;
					}while(last->next!=START);
					seclast->next=last->next;
					START->previous=seclast;
					free(last);
				   }
			   
	 }
	 return(START);
 }
struct node* delbyval(struct node *START,int val)
{
	if(START==NULL)
	{
		printf("List is empty");
	}
	else
	{           if(START->next==START)
	         {
			 
		       if(START->info==val)
		           START=delatbeg(START);
		           else
		            printf("Value not found ! \n");
		       }
		        else
		             if(START->previous->info==val)
		                 START=delatend(START);
		             else
		               {
		               	struct node *last,*seclast;
		               	 last=START;
		               	 do
		               	 {
		               	 	seclast=last;
		               	 	if(last->info==val)
		               	 	   { 
		               	 	     seclast->next=last->next;
		               	 	      last->next->previous=seclast;
		               	 	        free(last);
		               	 	        break;
		               	 	        
								   }
								   last=last->next;
								
							}while(last!=START);
							if(last==START)
							  printf("Value not found ! \n");
					   }
	}
	return(START);
}
	   		     
void traverse(struct node* START)
{
	if(START==NULL)
	   printf("List is empty");
	else
	 {
	 	struct node *p;
	 	p=START;
	 	do
	 	{
	 		printf("%d->",p->info);
	 		p=p->next;
		 }while(p!=START);
	 }
	 getch();
}

 int menu()
 {
 	printf("\n1. Insert at Beggining");
 	printf("\n2. Insert at end");
 	printf("\n3. Insert at position");
 	printf("\n4. Delete at beggining");
 	printf("\n5. Delete Last Node");
 	printf("\n6. Delete by value");
 	printf("\n7. Traverse");
 	printf("\n8. Exit");
 	
 	int ch;
 	printf("\n Enter your choice : ");
 	scanf("%d",&ch);
 	return(ch);
 }
 
 main()
 {
 	struct node *START=NULL;
 	int v,pos;
 	 while(1)
 	 {
 	 	system("cls");
 	 	switch(menu())
 	 	{
 	 		case 1: printf(" \n Enter the value : ");
 	 		scanf("%d",&v);
 	 		START=addatbeg(START,v);
 	 		traverse(START);
 	 		break;
 	 		
 	 		case 2: printf(" \n Enter the value : ");
 	 		scanf("%d",&v);
 	 		START=addatend(START,v);
 	 		traverse(START);
 	 		break;
 	 		
 	 		case 3:  printf(" \n Enter the position : ");
 	 		scanf("%d",&pos);
 	 		 printf(" \n Enter the value : ");
 	 		scanf("%d",&v);
 	 		START=addatpos(START,pos,v);
 	 		traverse(START);
 	 		break;
 	 		case 4: START=delatbeg(START);
 	 		       traverse(START);
 	 		       break;
 	 		       
 	 		case 5: START=delatend(START);
			        traverse(START);
					break;       
 	 		
 	 		case 6:  printf(" \n Enter the value : ");
 	 		scanf("%d",&v);
 	 		START=delbyval(START,v);
 	 		traverse(START);
 	 		break;
 	 		
 	 		case 7: traverse(START);
 	 		break;
 	 		
 	 		case 8: exit(1);
 	 		break;
 	 		
 	 		default : printf("Invalid Choice");
 	 		break;
		  }
	  }
 	
 }
